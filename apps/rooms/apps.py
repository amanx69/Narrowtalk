from django.apps import AppConfig


class RoomsConfig(AppConfig):
    name = 'apps.rooms'

    def ready(self) :
        import apps.rooms.signal