import os

from celery import Celery
# For installing the broker:
# https://docs.celeryq.dev/en/latest/getting-started/backends-and-brokers/rabbitmq.html#broker-rabbitmq
# https://www.rabbitmq.com/install-windows.html#chocolatey
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DagasServer.settings')

app = Celery('DagasServer')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')