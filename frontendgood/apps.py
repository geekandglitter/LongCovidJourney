from django.apps import AppConfig


class BlogExtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'



from django.apps import AppConfig


class frontendConfig(AppConfig):
    name = "frontend"
    verbose_name = "Front End"
