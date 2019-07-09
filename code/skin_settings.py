import os

SKIN_APPS = [
    'pgeusite.cmutuel.apps.cmConfig',
]

SITEBASE = "https://www.postgresql.eu"
ORG_NAME = "PostgreSQL Europe"
ORG_SHORTNAME = "PGEU"

# Modules
ENABLE_PG_COMMUNITY_AUTH = True
ENABLE_MEMBERSHIP = True
ENABLE_ELECTIONS = True
ENABLE_AUTO_ACCOUNTING = True

# Emails
DEFAULT_EMAIL = "webmaster@postgresql.eu"
SERVER_EMAIL = "webmaster@postgresql.eu"
TREASURER_EMAIL = "treasurer@postgresql.eu"
INVOICE_SENDER_EMAIL = "treasurer@postgresql.eu"
INVOICE_NOTIFICATION_RECEIVER = "treasurer@postgresql.eu"
SCHEDULED_JOBS_EMAIL = "webmaster@postgresql.eu"

# Ugh
EU_VAT = True
EU_VAT_HOME_COUNTRY = "FR"
EU_VAT_VALIDATE = True

# Invoice
INVOICE_PDF_BUILDER = 'pgeuinvoices.PGEUInvoice'
REFUND_PDF_BUILDER = 'pgeuinvoices.PGEURefund'
