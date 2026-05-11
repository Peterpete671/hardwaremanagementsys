from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        """Import signals when app is ready."""
        #Import audit signals to ensure they're registered
        import audit.signals
