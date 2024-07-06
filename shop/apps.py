from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"

    def ready(self):
        '''import both or doesn't work propperly'''
        from shop import signals
        from . import handlers
        