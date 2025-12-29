"""
Abonents app configuration.
"""

from django.apps import AppConfig


class AbonentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'abonents'
    verbose_name = 'Abonentlar'
    
    def ready(self):
        """Import signals when app is ready."""
        import abonents.signals  # noqa
