import django
from django.conf import settings

def setup_django_template_system():
    settings.configure()
    settings.TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates'
        }
    ]
    django.setup()


def percentage(percent, whole):
    return (percent * whole) / 100.0