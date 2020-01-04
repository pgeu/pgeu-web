from django import forms
from django.shortcuts import render
from django.template import Template, Context

from urllib.parse import urlencode
import csv
import datetime
from decimal import Decimal

from postgresqleu.util.payment.banktransfer import BaseManagedBankPayment
from postgresqleu.util.payment.banktransfer import BaseManagedBankPaymentForm
from postgresqleu.invoices.models import Invoice
from postgresqleu.invoices.util import register_bank_transaction

from pgeusite.cmutuel.models import CMutuelTransaction


class BackendCMutuelForm(BaseManagedBankPaymentForm):
    bank_file_uploads = True

    user = forms.CharField(required=True, label="User account", help_text="Username used to log in")
    password = forms.CharField(required=True, widget=forms.widgets.PasswordInput(render_value=True))

    managed_fields = ['user', 'password', ]
    managed_fieldsets = [
        {
            'id': 'cm',
            'legend': 'Credit Mutuel',
            'fields': ['user', 'password', ],
        }
    ]


class CMutuelPayment(BaseManagedBankPayment):
    backend_form_class = BackendCMutuelForm
    description = """
Pay using a direct IBAN bank transfer in EUR. We
<strong>strongly advice</strong> not using this method if
making a payment from outside the Euro-zone, as amounts
must be exact and all fees covered by sender.
"""
    upload_tooltip = """Go the CM website, select the account and click the download button for format <i>other</i>.

<b>Format:</b> CSV
<b>Format:</b> Excel XP and following
<b>Dates:</b> French long
<b>Field separator:</b> Semicolon
<b>Amounts in:</b> a single column
<b>Decimal separator:</b> point

Download a reasonable range of transactions, typically with a few days overlap.
""".replace("\n", "<br/>")

    def render_page(self, request, invoice):
        return render(request, 'cmutuel/payment.html', {
            'invoice': invoice,
        })

    def parse_uploaded_file(self, contents):
        reader = csv.reader(contents.splitlines(), delimiter=';')

        # Write everything to the database
        foundheader = False
        numrows = 0
        numtrans = 0
        numpending = 0
        for row in reader:
            if row[0] == 'Date':
                # Validaste the header
                colheaders = ['Date', 'Value date', 'Amount', 'Message', 'Balance']
                if len(row) != len(colheaders):
                    raise Exception("Invalid number of columns in input file. Got {}, expected {}.".format(len(row), len(colheaders)))
                for i in range(len(colheaders)):
                    if row[i] != colheaders[i]:
                        raise Exception("Invalid column {}. Got {}, expected {}.".format(i, row[i], colheaders[i]))
                foundheader = True
                continue
            if not foundheader:
                raise Exception("Header row missing in file")

            numrows += 1

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
                    numtrans += 1

                    # Also send the transaction into the main system. Unfortunately we don't
                    # know the sender.
                    # register_bank_transaction returns True if the transaction has been fully
                    # processed and thus don't need anything else, so we just consider it
                    # sent already.
                    if register_bank_transaction(self.method, trans.id, amount, description, ''):
                        trans.sent = True
                        trans.save()
                    else:
                        numpending += 1
            except Exception as e:
                # Re-raise but including the full row information
                raise Exception("Exception '{0}' when parsing row {1}".format(e, row))

        return (numrows, numtrans, numpending)
