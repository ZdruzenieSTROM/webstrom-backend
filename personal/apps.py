from django.apps import AppConfig


class PersonalConfig(AppConfig):
    name = 'personal'

    def ready(self):
        import personal.signals
