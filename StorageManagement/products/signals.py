# products/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from products.models import ProductRating, Product
from warehouses.models import Inventory
from django.db import models
from django.db import models
from .models import Product, ProductProperty  # اضافه کردن import مدل ProductProperty

    

@receiver(post_save, sender=ProductRating)
@receiver(post_delete, sender=ProductRating)
def update_product_avg_score(sender, instance, **kwargs):
    product = instance.product
    avg = product.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
    product.avg_score = round(avg, 2) if avg is not None else 0
    product.save()


@receiver([post_save, post_delete], sender=Inventory)
def update_product_total_stock(sender, instance, **kwargs):
    """
    سیگنال برای به روز رسانی total_stock در ProductProperty
    هنگامی که یک رکورد Inventory ذخیره یا حذف می‌شود
    """
    # محاسبه مجموع stockهای مربوط به این محصول در تمام انبارها
    total = Inventory.objects.filter(product=instance.product).aggregate(
        total_stock=models.Sum('stock')
    )['total_stock'] or 0
    
    # به روز رسانی فیلد total_stock در محصول مربوطه
    ProductProperty.objects.filter(pk=instance.product.pk).update(total_stock=total)
