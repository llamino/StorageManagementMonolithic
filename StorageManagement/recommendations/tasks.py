from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command
from django.utils import timezone

logger = get_task_logger(__name__)

@shared_task(
    name='recommendations.tasks.export_orders_to_csv',
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def export_orders_to_csv(self):
    """
    Task to export order data to CSV file.
    This task runs every hour and exports comprehensive order information including:
    - Customer details
    - Order information
    - Product details
    - Pricing information
    """
    try:
        logger.info(f"Starting order data export at {timezone.now()}")
        
        # Call the management command
        call_command('export_csv_from_models')
        
        logger.info("Successfully exported order data to CSV")
        return "Order data exported successfully"
            
    except Exception as exc:
        logger.error(f"Error exporting order data: {str(exc)}")
        self.retry(exc=exc)
