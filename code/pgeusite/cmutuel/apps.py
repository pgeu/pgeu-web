from django.apps import AppConfig


class cmConfig(AppConfig):
    name = 'pgeusite.cmutuel'
    verbose_name = 'Credit Mutuel'

    def ready(self):
        # Must be imported here since the class is loaded too early
        from postgresqleu.util.payment import register_payment_implementation

        register_payment_implementation('pgeusite.cmutuel.util.CMutuelPayment')
