import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'django_air.settings.dev')

app = Celery('django_air')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'client_flight_reminder_every_10_minute': {
        'task': 'client.tasks.flight_client_reminder',
        'schedule': crontab(minute='*/10')
    },
    'delete_purchases_if_not_paid': {
        'task': 'client.tasks.check_purchase_is_paid',
        'schedule': crontab(minute='*/1')
    },
    'pilot_flight_reminder_every_10_minute': {
        'task': 'staff.tasks.flight_pilot_reminder',
        'schedule': crontab(minute='*/10')
    },
}
