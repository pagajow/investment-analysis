from django.apps import AppConfig


class AnalysisappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analysisapp"
    
    def ready(self):
        import analysisapp.signals 
