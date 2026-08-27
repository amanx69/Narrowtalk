from django.apps import AppConfig


class ProfileConfig(AppConfig):
    name = 'apps.Profile'
    
    def ready(self) -> None:
        import apps.Profile.signal
