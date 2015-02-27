"""artlaasya apps"""

from django.apps import AppConfig



class ArtLaasyaAppConfig(AppConfig):

    name = 'artlaasya'
    verbose_name = 'ArtLaasya'

    def ready(self):
        #import signals
        import deepzoom.signals
        import artlaasya.signals