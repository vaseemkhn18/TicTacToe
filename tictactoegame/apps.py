from django.apps import AppConfig

class TictactoegameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tictactoegame'
    #new
    def ready(self):
        from . import job
        job.start_schedule()
