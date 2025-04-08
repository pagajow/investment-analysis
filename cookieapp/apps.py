from django.apps import AppConfig


class CookieappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cookieapp"

    def ready(self):
        import cookieapp.signals