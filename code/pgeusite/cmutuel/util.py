from django import forms
from django.shortcuts import render
from django.template import Template, Context
from django.db.models import Sum

from urllib.parse import urlencode

from postgresqleu.util.payment.banktransfer import BaseManagedBankPayment
from postgresqleu.util.payment.banktransfer import BaseManagedBankPaymentForm
from postgresqleu.invoices.models import Invoice, BankTransferFees


class BackendCMutuelForm(BaseManagedBankPaymentForm):
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

    def render_page(self, request, invoice):
        return render(request, 'cmutuel/payment.html', {
            'invoice': invoice,
        })
