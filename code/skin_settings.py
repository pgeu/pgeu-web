import os

SKIN_APPS = [
    'pgeusite.cmutuel',
]

SITEBASE = "https://www.postgresql.eu"
ORG_NAME = "PostgreSQL Europe"
ORG_SHORTNAME = "PGEU"

# Modules
ENABLE_PG_COMMUNITY_AUTH = True
ENABLE_MEMBERSHIP = True
ENABLE_ELECTIONS = True
ENABLE_TRUSTLY = True
ENABLE_AUTO_ACCOUNTING = True

# Emails
DEFAULT_EMAIL = "webmaster@postgresql.eu"
SERVER_EMAIL = "webmaster@postgresql.eu"
TREASURER_EMAIL = "treasurer@postgresql.eu"
INVOICE_SENDER_EMAIL = "treasurer@postgresql.eu"
MEMBERSHIP_SENDER_EMAIL = "webmaster@postgresql.eu"

# Membership
MEMBERSHIP_LENGTH = 2
MEMBERSHIP_COST = 10
def MEMBERSHIP_COUNTRY_VALIDATOR(country):
    if hasattr(country, 'europecountry'):
        return True
    return "Membership in PostgreSQL Europe is available to people living in geographical Europe. Exceptions to this may be provided on a case by case basis by the board. Please contact the board via email if you are seeing this message in error."


# Ugh
EU_VAT = True
EU_VAT_HOME_COUNTRY = "FR"
EU_VAT_VALIDATE = True

# Invoice
INVOICE_PDF_BUILDER = 'pgeuinvoices.PGEUInvoice'
REFUND_PDF_BUILDER = 'pgeuinvoices.PGEURefund'

# Paypal
PAYPAL_EMAIL = "paypal@postgresql.eu"
PAYPAL_RECEIVER = "paypal@postgresql.eu"
PAYPAL_DONATION_TEXT = "PostgreSQL Europe"

# CM balance fetching account
CM_USER_ACCOUNT = None
CM_USER_PASSWORD = None

# Load trustly keys
with open(os.path.join(os.path.dirname(__file__), 'trustly_public.pem'), 'r') as f:
    TRUSTLY_PUBLIC_KEY = f.read()
with open(os.path.join(os.path.dirname(__file__), 'trustly_private.pem'), 'r') as f:
    TRUSTLY_PRIVATE_KEY = f.read()
