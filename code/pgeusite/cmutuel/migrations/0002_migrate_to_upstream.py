# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmutuel', '0001_initial'),
        ('invoices', '0017_banksstatement'),
    ]

    operations = [
        # Transfer exisitng ledger entries to the general one
        migrations.RunSQL("""
INSERT INTO invoices_bankstatementrow (created, uniqueid, date, amount, description, balance, other, fromfile_id, method_id)
SELECT
  CURRENT_TIMESTAMP,
  NULL,
  opdate,
  amount,
  description,
  balance,
  jsonb_build_object('valdate', valdate),
  NULL,
  (SELECT id FROM invoices_invoicepaymentmethod WHERE classname='pgeusite.cmutuel.util.CMutuelPayment')
FROM cmutuel_cmutueltransaction
"""),
        # Update the existing payment entries
        migrations.RunSQL("""
UPDATE invoices_invoicepaymentmethod SET
  classname='postgresqleu.util.payment.banktransfer.GenericManagedBankPayment',
  config=config || '{"filetype": "cmutuel", "definition": "", "description": "Pay using a direct IBAN bank transfer in EUR. We <strong>strongly advice</strong> not using this method if making a payment from outside the Euro-zone, as amounts must be exact and all fees covered by sender."}'::jsonb
WHERE classname='pgeusite.cmutuel.util.CMutuelPayment'
        """)
    ]
