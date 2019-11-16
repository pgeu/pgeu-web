# Scrape the CM pages to fetch list of transactions
#
#
# Copyright (C) 2014-2019, PostgreSQL Europe
#
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max, Q
from django.conf import settings

import requests
import io
import datetime
import csv
import sys
from decimal import Decimal
from html.parser import HTMLParser


from postgresqleu.mailqueue.util import send_simple_mail
from postgresqleu.invoices.util import register_bank_transaction
from postgresqleu.invoices.models import InvoicePaymentMethod

from pgeusite.cmutuel.models import CMutuelTransaction


class FormHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_form = False
        self.target_url = None

    def handle_starttag(self, tag, attrs):
        if self.target_url:
            return
        if tag == 'form':
            for k, v in attrs:
                if k == 'action':
                    if v.find('telechargement.cgi?') >= 0:
                        self.in_form = True
                        self.target_url = v
                        return


class SessionWrapper(object):
    def __init__(self):
        self.session = requests.Session()

    def get(self, url):
        return self.session.get(url, allow_redirects=False)

    def post(self, url, postdict):
        return self.session.post(url, data=postdict, allow_redirects=False)

    def expect_redirect(self, fetchpage, redirectto, postdata=None, allow_200=True):
        if postdata:
            r = self.post(fetchpage, postdata)
        else:
            r = self.get(fetchpage)

        if not r.is_redirect:
            if allow_200 and r.status_code == 200:
                return ""
            raise CommandError("Supposed to receive redirect for %s, got %s" % (fetchpage, r.status_code))
        if not isinstance(redirectto, list):
            redirrectto = [redirectto, ]
        if not r.headers['Location'] in redirectto:
            raise CommandError("Received unexpected redirect from %s to '%s' (expected %s)" % (
                fetchpage, r.headers['Location'], redirectto))
        return r.headers['Location']


class Command(BaseCommand):
    help = 'Scrape the CM website for list of recent transactions'

    class ScheduledJob:
        scheduled_times = [datetime.time(9, 12), datetime.time(14, 12), datetime.time(19, 12)]

        @classmethod
        def should_run(self):
            return InvoicePaymentMethod.objects.filter(active=True, classname='pgeusite.cmutuel.util.CMutuelPayment').exists()

    def add_arguments(self, parser):
        parser.add_argument('-q', '--quiet', action='store_true')

    def handle(self, *args, **options):
        method = InvoicePaymentMethod.objects.get(active=True, classname='pgeusite.cmutuel.util.CMutuelPayment')
        pm = method.get_implementation()

        verbose = not options['quiet']

        sess = SessionWrapper()

        if verbose:
            self.stdout.write("Logging in...")

        sess.expect_redirect('https://www.creditmutuel.fr/en/authentification.html',
                             'https://www.creditmutuel.fr/en/banque/pageaccueil.html', {
                                 '_cm_user': pm.config('user'),
                                 '_cm_pwd': pm.config('password'),
                                 'flag': 'password',
                             })

        if verbose:
            self.stdout.write("Following a redirect chain for cookies")

        # Follow a redirect chain to collect more cookies
        sess.expect_redirect('https://www.creditmutuel.fr/en/banque/pageaccueil.html',
                             'https://www.creditmutuel.fr/en/banque/paci_engine/engine.aspx',
                             allow_200=True)

        # Download the form
        if verbose:
            self.stdout.write("Downloading form...")

        r = sess.get('https://www.creditmutuel.fr/en/banque/compte/telechargement.cgi')
        if r.status_code != 200:
            raise CommandError("Supposed to receive 200, got %s" % r.status_code)

        if verbose:
            self.stdout.write("Parsing form...")

        parser = FormHtmlParser()
        parser.feed(r.text)

        fromdate = CMutuelTransaction.objects.all().aggregate(max=Max('opdate'))
        if fromdate['max']:
            # Overlap with 1 week, just in case there are some old xacts. Yes, we might loose some,
            # but we don't really care :)
            fromdate = fromdate['max'] - datetime.timedelta(days=7)
        else:
            # No previous one, so just pick a date... This will only happen once..
            fromdate = datetime.date(2014, 1, 1)

        if verbose:
            self.stdout.write("Fetch report since {0}".format(fromdate))

        r = sess.post("https://www.creditmutuel.fr%s" % parser.target_url, {
            'data_formats_selected': 'csv',
            'data_formats_options_cmi_download': '0',
            'data_formats_options_ofx_format': '7',
            'Bool:data_formats_options_ofx_zonetiers': 'false',
            'CB:data_formats_options_ofx_zonetiers': 'on',
            'data_formats_options_qif_fileformat': '6',
            'ata_formats_options_qif_dateformat': '0',
            'data_formats_options_qif_amountformat': '0',
            'data_formats_options_qif_headerformat': '0',
            'Bool:data_formats_options_qif_zonetiers': 'false',
            'CB:data_formats_options_qif_zonetiers': 'on',
            'data_formats_options_csv_fileformat': '2',
            'data_formats_options_csv_dateformat': '0',
            'data_formats_options_csv_fieldseparator': '0',
            'data_formats_options_csv_amountcolnumber': '0',
            'data_formats_options_csv_decimalseparator': '1',
            'Bool:data_accounts_account_ischecked': 'false',
            'CB:data_accounts_account_ischecked': 'on',
            'data_daterange_value': 'range',
            '[t:dbt%3adate;]data_daterange_startdate_value': fromdate.strftime('%d/%m/%Y'),
            '[t:dbt%3adate;]data_daterange_enddate_value': '',
            '_FID_DoDownload.x': '57',
            '_FID_DoDownload.y': '17',
            'data_accounts_selection': '1',
            'data_formats_options_cmi_show': 'True',
            'data_formats_options_qif_show': 'True',
            'data_formats_options_excel_show': 'True',
            'data_formats_options_csv_show': 'True',
        })
        if r.status_code != 200:
            raise CommandError("Supposed to receive 200, got %s" % r.status_code)

        reader = csv.reader(r.text.splitlines(), delimiter=';')

        # Write everything to the database
        with transaction.atomic():
            for row in reader:
                if row[0] == 'Operation date' or row[0] == 'Date':
                    # This is just a header
                    continue
                try:
                    opdate = datetime.datetime.strptime(row[0], '%d/%m/%Y')
                    valdate = datetime.datetime.strptime(row[1], '%d/%m/%Y')
                    amount = Decimal(row[2])
                    description = row[3]
                    balance = Decimal(row[4])

                    if opdate.date() == datetime.date.today() and amount > 0 and description.startswith("VIR "):
                        # For incoming transfers we sometimes don't get the full transaction text
                        # right away. Because, reasons unknown. So if the transaction is actually
                        # dated today and it starts with VIR, we ignore it until we get to tomorrow.
                        continue

                    if not CMutuelTransaction.objects.filter(opdate=opdate, valdate=valdate, amount=amount, description=description).exists():
                        trans = CMutuelTransaction(opdate=opdate,
                                                   valdate=valdate,
                                                   amount=amount,
                                                   description=description,
                                                   balance=balance)
                        trans.save()

                        # Also send the transaction into the main system. Unfortunately we don't
                        # know the sender.
                        # register_bank_transaction returns True if the transaction has been fully
                        # processed and thus don't need anything else, so we just consider it
                        # sent already.
                        if register_bank_transaction(method, trans.id, amount, description, ''):
                            trans.sent = True
                            trans.save()
                except Exception as e:
                    sys.stderr.write("Exception '{0}' when parsing row {1}".format(e, row))

        # Now send things off if there is anything to send
        with transaction.atomic():
            if CMutuelTransaction.objects.filter(sent=False).exists():
                sio = io.StringIO()
                sio.write("One or more new transactions have been recorded in the Credit Mutuel account:\n\n")
                sio.write("%-10s  %15s  %s\n" % ('Date', 'Amount', 'Description'))
                sio.write("-" * 50)
                sio.write("\n")

                for cmt in CMutuelTransaction.objects.filter(sent=False).order_by('opdate'):
                    sio.write("%10s  %15s  %s\n" % (cmt.opdate, cmt.amount, cmt.description))
                    cmt.sent = True
                    cmt.save()

                sio.write("\n\nYou will want to go processes these at:\n{0}/admin/invoices/banktransactions/".format(settings.SITEBASE))

                send_simple_mail(settings.INVOICE_SENDER_EMAIL,
                                 settings.INVOICE_SENDER_EMAIL,
                                 'New Credit Mutuel transactions',
                                 sio.getvalue())
