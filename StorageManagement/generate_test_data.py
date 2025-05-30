import os
import django
import random
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StorageManagement.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker('fa_IR')

# Persian words for categories
CATEGORY_NAMES = [
    'پوشاک', 'کفش', 'اکسسوری', 'عینک', 'ساعت', 'کیف', 'کوله', 'کمربند',
    'روسری', 'شال', 'دستکش', 'جوراب', 'کلاه', 'کراوات', 'پیراهن'
]

# Persian words for colors
COLOR_NAMES = [
    'قرمز', 'آبی', 'سبز', 'زرد', 'مشکی', 'سفید', 'بنفش', 'صورتی',
    'نارنجی', 'قهوه‌ای', 'خاکستری', 'کرم', 'طلایی', 'نقره‌ای'
]

# Persian words for sizes
SIZE_NAMES = [
    'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL',
    '36', '37', '38', '39', '40', '41', '42', '43', '44', '45'
]

# Configuration for number of records to generate
CONFIG = {
    'users': 50,
    'categories': 10,
    'colors': 12,
    'sizes': 12,
    'employees': 20,
    'tasks': 30,
    'warehouses': 5,
    'suppliers': 15,
    'products': 50,
    'orders': 100,
    'order_items': 400,
    'product_ratings': 1000,
    'comments': 100,
    'product_properties': 300,
    'inventory_suppliers': 50,
    'purchase_orders': 30,
    'purchase_order_details': 100,
    'addresses': 70,
    'profiles': 40,
    'inventories': 200,
    'category_discounts': 20,
    'product_discounts': 30,
    'user_discounts': 40,
}

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

def generate_base_data():
    """Generate base data for independent models"""
    logger.info("Starting base data generation...")
    
    # Generate Categories
    categories = []
    available_categories = CATEGORY_NAMES.copy()
    for _ in range(CONFIG['categories']):
        if not available_categories:
            break
        category_name = random.choice(available_categories)
        available_categories.remove(category_name)
        category = Category.objects.create(
            name=category_name
        )
        categories.append(category)
    logger.info(f"Generated {len(categories)} categories")

    # Generate Colors
    colors = []
    available_colors = COLOR_NAMES.copy()
    for _ in range(CONFIG['colors']):
        if not available_colors:
            break
        color_name = random.choice(available_colors)
        available_colors.remove(color_name)
        color = Color.objects.create(
            name=color_name
        )
        colors.append(color)
    logger.info(f"Generated {len(colors)} colors")

    # Generate Sizes
    sizes = []
    available_sizes = SIZE_NAMES.copy()
    for _ in range(CONFIG['sizes']):
        if not available_sizes:
            break
        size_name = random.choice(available_sizes)
        available_sizes.remove(size_name)
        size = Size.objects.create(
            name=size_name
        )
        sizes.append(size)
    logger.info(f"Generated {len(sizes)} sizes")

    # Generate Warehouses
    warehouses = []
    for i in range(CONFIG['warehouses']):
        warehouse = Warehouse.objects.create(
            name=f"انبار {i+1}",
            address=fake.address(),
            is_full=random.choice([True, False])
        )
        warehouses.append(warehouse)
    logger.info(f"Generated {len(warehouses)} warehouses")

    # Generate Suppliers
    suppliers = []
    for i in range(CONFIG['suppliers']):
        supplier = Supplier.objects.create(
            name=f"تامین کننده {i+1}",
            phone_number=fake.phone_number(),
            address=fake.address(),
            is_active=random.choice([True, False])
        )
        suppliers.append(supplier)
    logger.info(f"Generated {len(suppliers)} suppliers")

    return categories, colors, sizes, warehouses, suppliers

def generate_user_data():
    """Generate user related data"""
    logger.info("Starting user data generation...")
    
    users = []
    for _ in range(CONFIG['users']):
        # Generate a valid 11-digit phone number
        phone_number = '09' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        user = User.objects.create_user(
            email=fake.email(),
            phone_number=phone_number,
            password='testpass123'
        )
        users.append(user)
    logger.info(f"Generated {len(users)} users")

    # Update existing profiles (created by signal)
    profiles = []
    for user in users:
        profile = user.profile  # Get the profile created by the signal
        profile.first_name = fake.first_name()
        profile.last_name = fake.last_name()
        profile.bio = fake.text(max_nb_chars=200)
        profile.save()
        profiles.append(profile)
    logger.info(f"Updated {len(profiles)} profiles")

    # Generate Addresses
    addresses = []
    for user in users:
        address = Address.objects.create(
            user=user,
            province=fake.state(),
            city=fake.city(),
            street=fake.street_name(),
            alley=fake.street_suffix(),
            house_number=str(random.randint(1, 999))
        )
        addresses.append(address)
    logger.info(f"Generated {len(addresses)} addresses")

    return users, profiles, addresses

def generate_product_data(categories, colors, sizes):
    """Generate product related data"""
    logger.info("Starting product data generation...")
    
    products = []
    for i in range(CONFIG['products']):
        product = Product.objects.create(
            name=f"محصول {i+1}",
            description=fake.text(max_nb_chars=500),
            avg_score=random.uniform(0, 5)
        )
        # Add random categories
        for category in random.sample(categories, random.randint(1, 3)):
            product.categories.add(category)
        products.append(product)
    logger.info(f"Generated {len(products)} products")

    # Generate Product Properties with unique combinations
    properties = []
    for product in products:
        # Create a set to track used combinations
        used_combinations = set()
        # Generate 2-4 unique properties for each product
        num_properties = random.randint(2, 4)
        attempts = 0
        max_attempts = 50  # Prevent infinite loops
        
        while len(used_combinations) < num_properties and attempts < max_attempts:
            size = random.choice(sizes)
            color = random.choice(colors)
            combination = (product, size, color)
            
            if combination not in used_combinations:
                try:
                    property = ProductProperty.objects.create(
                        product=product,
                        size=size,
                        color=color,
                        buy_price=random.uniform(50000, 5000000),
                        sell_price=random.uniform(100000, 10000000),
                        weight=random.uniform(0.1, 10.0),
                        can_sale=random.choice([True, False]),
                        total_stock=random.randint(0, 100)
                    )
                    properties.append(property)
                    used_combinations.add(combination)
                except Exception as e:
                    logger.warning(f"Failed to create property: {str(e)}")
            attempts += 1
            
    logger.info(f"Generated {len(properties)} product properties")

    return products, properties

def generate_order_data(users, products):
    """Generate order related data"""
    logger.info("Starting order data generation...")
    
    # Get all product properties
    product_properties = ProductProperty.objects.all()
    if not product_properties:
        logger.warning("No product properties found. Skipping order generation.")
        return [], []
    
    orders = []
    for _ in range(CONFIG['orders']):
        order = Order.objects.create(
            user=random.choice(users),
            total_price=random.uniform(100000, 10000000),
            status=random.choice(['pending', 'paid', 'shipped', 'delivered', 'canceled']),
            payment_method=random.choice(['online', 'cash', 'wallet']),
            shipping_price=random.uniform(10000, 100000),
            tax=random.uniform(5000, 50000),
            discount=random.uniform(0, 100000),
            notes=fake.text(max_nb_chars=200)
        )
        orders.append(order)
    logger.info(f"Generated {len(orders)} orders")

    # Generate Order Items
    order_items = []
    for order in orders:
        for _ in range(random.randint(1, 9)):
            product_property = random.choice(product_properties)
            order_item = OrderItem.objects.create(
                order=order,
                product=product_property,
                quantity=random.randint(1, 10),
                price=product_property.sell_price or random.uniform(10000, 1000000),
                discount=random.uniform(0, 50000)
            )
            order_items.append(order_item)
    logger.info(f"Generated {len(order_items)} order items")

    return orders, order_items

def generate_supplier_related_data(suppliers, categories, colors, sizes):
    """Generate supplier related data"""
    logger.info("Starting supplier related data generation...")
    
    # Generate Category Suppliers
    category_suppliers = []
    for _ in range(CONFIG['categories']):
        category_supplier = CategorySupplier.objects.create(
            name=f"تامین کننده دسته {_+1}"
        )
        category_suppliers.append(category_supplier)
    logger.info(f"Generated {len(category_suppliers)} category suppliers")

    # Generate Color Suppliers
    color_suppliers = []
    for _ in range(CONFIG['colors']):
        color_supplier = ColorSupplier.objects.create(
            name=f"تامین کننده رنگ {_+1}"
        )
        color_suppliers.append(color_supplier)
    logger.info(f"Generated {len(color_suppliers)} color suppliers")

    # Generate Size Suppliers
    size_suppliers = []
    for _ in range(CONFIG['sizes']):
        size_supplier = SizeSupplier.objects.create(
            name=f"تامین کننده سایز {_+1}"
        )
        size_suppliers.append(size_supplier)
    logger.info(f"Generated {len(size_suppliers)} size suppliers")

    # Generate Product Detail Suppliers
    product_suppliers = []
    for _ in range(CONFIG['suppliers']):
        product_supplier = ProductDetailSupplier.objects.create(
            name=f"محصول تامین کننده {_+1}",
            description=fake.text(max_nb_chars=500)
        )
        # Add random categories
        for category in random.sample(category_suppliers, random.randint(1, 3)):
            product_supplier.categories.add(category)
        product_suppliers.append(product_supplier)
    logger.info(f"Generated {len(product_suppliers)} product suppliers")

    # Generate Inventory Suppliers
    inventory_suppliers = []
    for supplier in suppliers:
        for product in random.sample(product_suppliers, random.randint(1, 5)):
            inventory_supplier = InventorySupplier.objects.create(
                supplier=supplier,
                product=product,
                stock=random.randint(0, 100),
                color=random.choice(color_suppliers) if random.choice([True, False]) else None,
                size=random.choice(size_suppliers) if random.choice([True, False]) else None,
                weight=random.uniform(0.1, 10.0) if random.choice([True, False]) else None,
                price=random.randint(10000, 1000000)
            )
            inventory_suppliers.append(inventory_supplier)
    logger.info(f"Generated {len(inventory_suppliers)} inventory suppliers")

def generate_discount_data(categories, products, users):
    """Generate discount related data"""
    logger.info("Starting discount data generation...")
    
    # Generate Category Discounts
    for _ in range(CONFIG['category_discounts']):
        CategoryDiscount.objects.create(
            name=f"تخفیف دسته {_+1}",
            description=fake.text(max_nb_chars=200),
            discount_type='percentage',
            value=random.randint(5, 50),
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=random.randint(1, 30)),
            is_active=True,
            category=random.choice(categories)
        )
    logger.info(f"Generated {CONFIG['category_discounts']} category discounts")

    # Generate Product Discounts
    for _ in range(CONFIG['product_discounts']):
        ProductDiscount.objects.create(
            name=f"تخفیف محصول {_+1}",
            description=fake.text(max_nb_chars=200),
            discount_type='percentage',
            value=random.randint(5, 50),
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=random.randint(1, 30)),
            is_active=True,
            product=random.choice(products)
        )
    logger.info(f"Generated {CONFIG['product_discounts']} product discounts")

    # Generate User Discounts
    for _ in range(CONFIG['user_discounts']):
        UserDiscount.objects.create(
            name=f"تخفیف کاربر {_+1}",
            description=fake.text(max_nb_chars=200),
            discount_type='percentage',
            value=random.randint(5, 50),
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=random.randint(1, 30)),
            is_active=True,
            user=random.choice(users),
            min_purchase_amount=random.uniform(100000, 1000000),
            max_discount_amount=random.uniform(50000, 500000)
        )
    logger.info(f"Generated {CONFIG['user_discounts']} user discounts")

def generate_comment_and_rating_data(users, products):
    """Generate comment and rating data"""
    logger.info("Starting comment and rating data generation...")
    
    # Generate Comments
    comments = []
    for _ in range(CONFIG['comments']):
        comment = Comment.objects.create(
            product=random.choice(products),
            user=random.choice(users),
            title=fake.sentence(),
            text=fake.text(max_nb_chars=500)
        )
        comments.append(comment)
    logger.info(f"Generated {len(comments)} comments")

    # Generate Product Ratings with unique user-product combinations
    ratings = []
    used_combinations = set()
    attempts = 0
    max_attempts = CONFIG['product_ratings'] * 2  # Allow some extra attempts

    while len(ratings) < CONFIG['product_ratings'] and attempts < max_attempts:
        user = random.choice(users)
        product = random.choice(products)
        combination = (user.id, product.name)  # Using name as it's the primary key

        if combination not in used_combinations:
            try:
                rating = ProductRating.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(1, 5)
                )
                ratings.append(rating)
                used_combinations.add(combination)
            except Exception as e:
                logger.warning(f"Failed to create rating: {str(e)}")
        attempts += 1

    logger.info(f"Generated {len(ratings)} product ratings")

    return comments, ratings

def generate_task_and_employee_data(warehouses):
    """Generate task and employee data"""
    logger.info("Starting task and employee data generation...")
    
    # Generate Tasks
    tasks = []
    for i in range(CONFIG['tasks']):
        task = Task.objects.create(
            title=f"وظیفه {i+1}",
            description=fake.text(max_nb_chars=200)
        )
        tasks.append(task)
    logger.info(f"Generated {len(tasks)} tasks")

    # Generate Employees
    employees = []
    for warehouse in warehouses:
        # Create manager
        manager = Employee.objects.create(
            warehouse=warehouse,
            name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number='09' + ''.join([str(random.randint(0, 9)) for _ in range(9)]),
            national_code=''.join([str(random.randint(0, 9)) for _ in range(10)]),
            image=None  # You might want to add actual image handling here
        )
        employees.append(manager)

        # Create regular employees
        for _ in range(random.randint(2, 5)):
            employee = Employee.objects.create(
                warehouse=warehouse,
                manager=manager,
                name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number='09' + ''.join([str(random.randint(0, 9)) for _ in range(9)]),
                national_code=''.join([str(random.randint(0, 9)) for _ in range(10)]),
                image=None
            )
            employees.append(employee)

            # Assign random tasks to employee
            for task in random.sample(tasks, random.randint(1, 3)):
                TaskForEmployee.objects.create(
                    employee=employee,
                    task=task,
                    is_done=random.choice([True, False])
                )
    logger.info(f"Generated {len(employees)} employees")

    return tasks, employees

def generate_inventory_data(warehouses, product_properties):
    """Generate inventory data"""
    logger.info("Starting inventory data generation...")
    
    inventories = []
    for warehouse in warehouses:
        # Calculate how many properties to use (between 1 and all available)
        num_properties = min(len(product_properties), random.randint(1, 5))
        selected_properties = random.sample(product_properties, num_properties)
        
        for product_property in selected_properties:
            inventory = Inventory.objects.create(
                warehouse=warehouse,
                product=product_property,
                stock=random.randint(0, 100)
            )
            inventories.append(inventory)
    logger.info(f"Generated {len(inventories)} inventory records")

    return inventories

def generate_purchase_order_data(suppliers, warehouses, inventory_suppliers):
    """Generate purchase order data"""
    logger.info("Starting purchase order data generation...")
    
    purchase_orders = []
    for _ in range(CONFIG['purchase_orders']):
        supplier = random.choice(suppliers)
        warehouse = random.choice(warehouses)
        total_price = random.uniform(1000000, 10000000)
        
        purchase_order = PurchaseOrderFromSupplier.objects.create(
            supplier=supplier,
            warehouse=warehouse,
            expected_delivery_date=timezone.now() + timedelta(days=random.randint(1, 30)),
            total_price_order=total_price,
            is_applied_to_warehouse=random.choice([True, False])
        )
        purchase_orders.append(purchase_order)

        # Generate purchase order details
        for _ in range(random.randint(1, 5)):
            inventory_supplier = random.choice(inventory_suppliers)
            # Ensure quantity doesn't exceed available stock
            max_quantity = inventory_supplier.stock
            quantity = random.randint(1, max(1, max_quantity))  # Use at least 1 if stock is 0
            price_per_unit = inventory_supplier.price
            total_price_item = price_per_unit * quantity

            try:
                PurchaseOrderDetails.objects.create(
                    purchase_order_id=purchase_order,
                    product_in_supplier=inventory_supplier,
                    quantity_ordered=quantity,
                    price_per_unit=price_per_unit,
                    total_price_item=total_price_item
                )
            except Exception as e:
                logger.warning(f"Failed to create purchase order detail: {str(e)}")
                continue

    logger.info(f"Generated {len(purchase_orders)} purchase orders")

    return purchase_orders



def main():
    """Main function to generate all test data"""
    try:
        logger.info("Starting test data generation...")
        
        # Generate base data
        categories, colors, sizes, warehouses, suppliers = generate_base_data()
        
        # Generate user related data
        users, profiles, addresses = generate_user_data()
        
        # Generate product related data
        products, properties = generate_product_data(categories, colors, sizes)
        
        # Generate order related data
        orders, order_items = generate_order_data(users, products)
        
        # Generate supplier related data
        generate_supplier_related_data(suppliers, categories, colors, sizes)
        
        # Generate discount data
        generate_discount_data(categories, products, users)

        # Generate comment and rating data
        comments, ratings = generate_comment_and_rating_data(users, products)

        # Generate task and employee data
        tasks, employees = generate_task_and_employee_data(warehouses)

        # Generate inventory data
        inventories = generate_inventory_data(warehouses, properties)

        # Generate purchase order data
        inventory_suppliers = InventorySupplier.objects.all()
        purchase_orders = generate_purchase_order_data(suppliers, warehouses, inventory_suppliers)
        
        logger.info("Test data generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error generating test data: {str(e)}")
        raise

if __name__ == "__main__":
    main()
