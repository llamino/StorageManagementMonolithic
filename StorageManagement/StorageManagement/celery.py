import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StorageManagement.settings')

app = Celery('StorageManagement')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'update-order-recommendations': {
        'task': 'recommendations.tasks.update_dashboard_stats_task',
        'schedule': crontab(hour='*/1'),  # Run every hour
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 