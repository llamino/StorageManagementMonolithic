# orders/models.py
from django.db import models
from users.models import User, Address
from products.models import ProductProperty
from warehouses.models import Inventory
from django.urls import reverse
from discounts.services import DiscountService


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('canceled', 'لغو شده'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('online', 'پرداخت آنلاین'),
        ('cash', 'پرداخت نقدی'),
        ('wallet', 'کیف پول'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='online')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='orders')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_code = models.CharField(max_length=10, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_reason = models.TextField(blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    tracking_code = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.user}'

    def get_absolute_url(self):
        return reverse('admin:orders_order_change', args=[str(self.id)])

    def calculate_total_price(self):
        """محاسبه مجموع قیمت تمام آیتم‌های سفارش"""
        if not self.pk:  # اگر سفارش هنوز ذخیره نشده
            return 0
        return sum(item.total_price for item in self.items.all())


    def calculate_discount_amount(self):
        self.discount_amount = 0
        self.discount_reason = None
        if self.discount_code:
            discount_amount, discount_reason = DiscountService.calculate_discount_code_amount(self,self.discount_code, self.total_price)
            if discount_amount:
                self.discount_amount = discount_amount
                self.discount_reason = discount_reason
            else:
                self.discount_code = None

    def calculate_final_price(self):
        self.calculate_discount_amount()
        """محاسبه قیمت نهایی با احتساب مالیات، هزینه حمل و تخفیف"""
        return (self.total_price + self.tax + self.shipping_price) - self.discount_amount

    def save(self, *args, **kwargs):
        # فقط اگر سفارش از قبل ذخیره شده، قیمت‌ها را محاسبه کن
        if self.pk:
            self.total_price = self.calculate_total_price()
            self.final_price = self.calculate_final_price()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductProperty, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_reason = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def __str__(self):
        return f'{self.order.id} - {self.product}'

    def calculate_orderitem_discount(self):
        discount_amount, discount_reason = DiscountService.get_product_discount(self.product.product, self.price)
        if discount_amount:
            self.discount_amount = discount_amount
            self.discount_reason = discount_reason

    def calculate_total_price(self):
        self.calculate_orderitem_discount()
        return (self.price - self.discount_amount) * self.quantity


    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
        self.order.save()


