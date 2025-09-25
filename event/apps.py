from django.apps import AppConfig

class EventConfig(AppConfig):
    """
    Configuration class for the 'event' application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event'

    def ready(self):
        """
        This method is called by Django when the application is ready.
        We import our signals file here to ensure that the signal handlers
        (for notifications, certificate generation, etc.) are connected and active.
        """
        import event.signals