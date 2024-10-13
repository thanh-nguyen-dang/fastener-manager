from django.apps import AppConfig


class FastenerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # For Django 3.2 and above
    name = 'fastener_app'
    verbose_name = 'Fastener App'  # Optional: A human-readable name for the admin interface

    def ready(self):
        # Optional: Import signal handlers or perform app initialization here
        # from . import signals
        pass
