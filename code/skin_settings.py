import os

SKIN_APPS=[
    'pgeusite.cmutuel',
]

SITEBASE="https://www.postgresql.eu"
ORG_NAME="PostgreSQL Europe"
ORG_SHORTNAME="PGEU"

# Modules
ENABLE_PG_COMMUNITY_AUTH=True
ENABLE_MEMBERSHIP=True
ENABLE_ELECTIONS=True
ENABLE_TRUSTLY=True
ENABLE_AUTO_ACCOUNTING=True

# Emails
DEFAULT_EMAIL="webmaster@postgresql.eu"
TREASURER_EMAIL="treasurer@postgresql.eu"
INVOICE_SENDER_EMAIL="treasurer@postgresql.eu"
MEMBERSHIP_SENDER_EMAIL="webmaster@postgresql.eu"

# Ugh
EU_VAT=True
EU_VAT_HOME_COUNTRY="FR"
EU_VAT_VALIDATE=True

# Paypal
PAYPAL_EMAIL="paypal@postgresql.eu"
PAYPAL_RECEIVER="paypal@postgresql.eu"
PAYPAL_DONATION_TEXT="PostgreSQL Europe"

# CM balance fetching account
CM_USER_ACCOUNT=None
CM_USER_PASSWORD=None

# Load trustly keys
with open(os.path.join(os.path.dirname(__file__), 'trustly_public.pem'), 'r') as f:
    TRUSTLY_PUBLIC_KEY=f.read()
with open(os.path.join(os.path.dirname(__file__), 'trustly_private.pem'), 'r') as f:
    TRUSTLY_PRIVATE_KEY=f.read()
