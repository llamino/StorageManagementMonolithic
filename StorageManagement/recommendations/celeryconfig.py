from celery.schedules import crontab

# Task routing
task_routes = {
    'recommendations.tasks.*': {'queue': 'recommendations'},
}

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Beat schedule
beat_schedule = {
    'export-orders-to-csv': {
        'task': 'recommendations.tasks.export_orders_to_csv',
        'schedule': crontab(hour='*/1'),  # Run every hour
        'options': {'queue': 'recommendations'}
    },
} 