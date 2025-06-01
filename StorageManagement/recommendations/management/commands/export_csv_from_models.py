
import csv
import logging
from django.core.management.base import BaseCommand
from django.db.models import Q

# Import models
from users.models import User, Profile, Address
from products.models import (
    Category, Color, Size, Product, ProductProperty,
    ProductRating, Comment
)
from orders.models import Order, OrderItem
from suppliers.models import (
    Supplier, SizeSupplier, ColorSupplier, CategorySupplier,
    InventorySupplier, ProductDetailSupplier
)
from warehouses.models import Warehouse, Task, Employee, Inventory, PurchaseOrderFromSupplier, PurchaseOrderDetails, TaskForEmployee
from discounts.models import CategoryDiscount, ProductDiscount, UserDiscount

logger = logging.getLogger(__name__)


def add_data_to_csv():
    # Define CSV file path
    csv_file_path = 'recommendations/data/order_items_data.csv'
    
    # Define CSV headers
    headers = [
        # User Information
        'user_id', 'user_email', 'user_phone', 'first_name', 'last_name',
        # Address Information
        'province', 'city',
        # Product Information
        'product_name', 'product_avg_score', 'product_categories',
        # Product Property Information
        'size', 'color', 'buy_price', 'sell_price', 'weight', 'can_sale', 'total_stock',
        # Order Information
        'order_id', 'order_status', 'payment_method', 'order_total_price', 'order_discount',
        'order_tax', 'order_shipping_price', 'order_final_price', 'order_created_at',
        'order_paid_at', 'order_shipped_at', 'order_tracking_code',
        # Order Item Information
        'order_item_quantity', 'order_item_price', 'order_item_discount',
        'order_item_total_price',
        # Rating Information
        'user_rating', 'rating_date'
    ]
    
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            # Get all order items with related data
            order_items = OrderItem.objects.select_related(
                'order__user',
                'product__product',
                'product__size',
                'product__color'
            ).prefetch_related(
                'product__product__categories',
                'order__user__addresses'  # Add prefetch for user addresses
            )
            
            for index, item in enumerate(order_items):
                if index == 15:
                    break
                # Get user rating for this product if exists
                try:
                    rating = ProductRating.objects.get(
                        user=item.order.user,
                        product=item.product.product
                    )
                    user_rating = rating.rating
                    rating_date = rating.rating_date
                except ProductRating.DoesNotExist:
                    user_rating = None
                    rating_date = None
                
                # Get product categories as comma-separated string
                categories = ', '.join([cat.name for cat in item.product.product.categories.all()])
                
                # Get user's primary address (first address in the list)
                user_address = None
                if item.order.user and hasattr(item.order.user, 'addresses'):
                    addresses = item.order.user.addresses.all()
                    if addresses.exists():
                        user_address = addresses.first()
                
                # Prepare row data
                row_data = {
                    # User Information
                    'user_id': item.order.user.id if item.order.user else None,
                    'user_email': item.order.user.email if item.order.user else None,
                    'user_phone': item.order.user.phone_number if item.order.user else None,
                    'first_name': item.order.user.profile.first_name if item.order.user and hasattr(item.order.user, 'profile') else None,
                    'last_name': item.order.user.profile.last_name if item.order.user and hasattr(item.order.user, 'profile') else None,
                    
                    # Address Information
                    'province': user_address.province if user_address else None,
                    'city': user_address.city if user_address else None,
 
                    
                    # Product Information
                    'product_name': item.product.product.name if item.product else None,
                    # 'product_description': item.product.product.description if item.product else None,
                    'product_avg_score': item.product.product.avg_score if item.product else None,
                    'product_categories': categories,
                    
                    # Product Property Information
                    'size': item.product.size.name if item.product and item.product.size else None,
                    'color': item.product.color.name if item.product and item.product.color else None,
                    'buy_price': item.product.buy_price if item.product else None,
                    'sell_price': item.product.sell_price if item.product else None,
                    'weight': item.product.weight if item.product else None,
                    'can_sale': item.product.can_sale if item.product else None,
                    'total_stock': item.product.total_stock if item.product else None,
                    
                    # Order Information
                    'order_id': item.order.id,
                    'order_status': item.order.status,
                    'payment_method': item.order.payment_method,
                    'order_total_price': item.order.total_price,
                    'order_discount': item.order.discount,
                    'order_tax': item.order.tax,
                    'order_shipping_price': item.order.shipping_price,
                    'order_final_price': item.order.final_price,
                    'order_created_at': item.order.created_at,
                    'order_paid_at': item.order.paid_at,
                    'order_shipped_at': item.order.shipped_at,
                    'order_tracking_code': item.order.tracking_code,
                    
                    # Order Item Information
                    'order_item_quantity': item.quantity,
                    'order_item_price': item.price,
                    'order_item_discount': item.discount,
                    'order_item_total_price': item.total_price,
                    
                    # Rating Information
                    'user_rating': user_rating,
                    'rating_date': rating_date
                }
                
                writer.writerow(row_data)
                
        logger.info(f"Successfully exported data to {csv_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting data to CSV: {str(e)}")
        return False


class Command(BaseCommand):
    help = "Export important data from models and import to csv file."

    def handle(self, *args, **options):
        add_data_to_csv()

