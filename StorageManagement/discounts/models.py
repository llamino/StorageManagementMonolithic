# discount/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.exceptions import ValidationError

from products.models import Product, Category
from users.models import User

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        """اعتبارسنجی مقادیر تخفیف"""
        if self.discount_type == 'percentage' and self.value > 100:
            raise ValidationError('تخفیف درصدی نمی‌تواند بیش از 100% باشد')
        if self.value < 0:
            raise ValidationError('مقدار تخفیف نمی‌تواند منفی باشد')
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('تاریخ شروع باید قبل از تاریخ پایان باشد')

    def save(self, *args, **kwargs):
        """فراخوانی clean قبل از ذخیره"""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_discount_type_display()}"

    def calculate_discount(self, price):
        if self.discount_type == 'percentage':
            return (price * self.value) / 100
        return self.value

class ProductDiscount(Discount):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts')

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class CategoryDiscount(Discount):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='discounts')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class UserDiscount(Discount):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discounts')
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def calculate_discount(self, price):
        if price < self.min_purchase_amount:
            return 0
        
        discount = super().calculate_discount(price)
        if self.max_discount_amount and discount > self.max_discount_amount:
            return self.max_discount_amount
        return discount



