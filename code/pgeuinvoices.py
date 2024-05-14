# -*- coding: utf-8 -*-
import os
from django.conf import settings

from postgresqleu.util.misc.baseinvoice import BaseInvoice, BaseRefund


class PGEUBase(object):
    logo = os.path.join(settings.PROJECT_ROOT, '../media/img/PostgreSQL_logo.1color_blue.300x300.png')
    headertext = """PostgreSQL Europe
61 rue de Lyon
75012 PARIS
France
SIREN 823839535
VAT# FR36823839535
"""
    sendertext = """Your contact:
Function: PostgreSQL Europe Treasurer
E-mail: treasurer@postgresql.eu"""

    bankinfotext = """CCM PARIS 1-2 LOUVRE MONTORGUEIL
28 RUE ETIENNE MARCEL
75002 PARIS
FRANCE
IBAN: FR76 1027 8060 3100 0205 2290 114
BIC: CMCIFR2A
"""

    paymentterms = """Penalty for late payment: Three times the French Legal Interest Rate on the due amount.
Compensation due for any recovery costs incurred: €40
Discount for prepayment: None.
"""


class PGEUInvoice(PGEUBase, BaseInvoice):
    pass


class PGEURefund(PGEUBase, BaseRefund):
    pass
