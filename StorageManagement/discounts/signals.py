# discounts/signals.py

import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from discounts.models import CategoryUserDiscount, UserDiscount


def generate_random_code(length=8):
    """تولید کد تخفیف تصادفی با حذف کاراکترهای مشابه"""
    # حذف کاراکترهای مشابه برای جلوگیری از اشتباه (مثل 0 و O، 1 و I)
    chars = (
        string.ascii_uppercase.replace('O', '').replace('I', '') +
        string.digits.replace('0', '').replace('1', '')
    )
    return ''.join(random.choices(chars, k=length))


@receiver(post_save, sender=CategoryUserDiscount)
def create_discountcode_category_user_discount(sender, instance, created, **kwargs):
    if created and not instance.discount_code:
        max_attempts = 100
        for _ in range(max_attempts):
            code = generate_random_code()
            if not CategoryUserDiscount.objects.filter(discount_code=code).exists():
                with transaction.atomic():
                    instance.discount_code = code
                    instance.save(update_fields=['discount_code'])
                break
        else:
            raise ValueError("Failed to generate unique discount code after {} attempts".format(max_attempts))


@receiver(post_save, sender=UserDiscount)
def create_discountcode_user(sender, instance, created, **kwargs):
    if created and not instance.discount_code:
        max_attempts = 100
        for _ in range(max_attempts):
            code = generate_random_code()
            if not UserDiscount.objects.filter(discount_code=code).exists():
                with transaction.atomic():
                    instance.discount_code = code
                    instance.save(update_fields=['discount_code'])
                break
        else:
            raise ValueError("Failed to generate unique discount code after {} attempts".format(max_attempts))