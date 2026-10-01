from django.apps import AppConfig


class ChatsConfig(AppConfig):
    name = 'apps.Chats'

    def ready(self):
        import apps.Chats.signals