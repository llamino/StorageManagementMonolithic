# products/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from products.models import ProductRating, Product

@receiver(post_save, sender=ProductRating)
@receiver(post_delete, sender=ProductRating)
def update_product_avg_score(sender, instance, **kwargs):
    product = instance.product
    avg = product.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
    product.avg_score = round(avg, 2) if avg is not None else 0
    product.save()
