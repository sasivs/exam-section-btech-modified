from django.apps import AppConfig


class BTCoOrdinatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BTco_ordinator'

    def ready(self):
        import BTco_ordinator.signals
