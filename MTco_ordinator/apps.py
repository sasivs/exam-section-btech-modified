from django.apps import AppConfig


class MtcoOrdinatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MTco_ordinator'
    
    def ready(self):
        import MTco_ordinator.signals
