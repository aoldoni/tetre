import django
from django.conf import settings


def setup_django_template_system():
    """Initialises the Django templating system as to be used standalone.
    """
    settings.configure()
    settings.TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates'
        }
    ]
    django.setup()


def percentage(percent, whole):
    """Simple method for percentage calculation.

    Args:
        percent: percent value being chased.
        whole: The whole value.

    Returns:
        The result percentage value.
    """
    return (percent * whole) / 100.0
