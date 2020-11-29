from django.apps import AppConfig


class PersonalConfig(AppConfig):
    # pylint: disable=C0415
    # pylint: disable=W0611
    name = 'personal'

    def ready(self):
        import personal.signals
