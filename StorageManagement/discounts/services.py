# discounts/services.py

from celery.beat import Service  # discount/services.py
from django.db.models import Sum
from django.utils import timezone
from discounts.models import ProductDiscount, CategoryUserDiscount, UserDiscount
from products.models import ProductProperty

class DiscountService():
    @staticmethod
    def get_product_discount(product, price):
        discounts = ProductDiscount.objects.filter(
            product=product,
            end_date__gt=timezone.now(),
            is_active=True
        )
        best_discount = None
        best_amount = 0
        for discount in discounts:
            amount = discount.calculate_discount(price)
            if amount > best_amount:
                best_amount = amount
                best_discount = discount

        if best_discount:
            return best_amount, best_discount.discount_reason
        return 0, None

    @staticmethod
    def calculate_category_discount(order_obj, category_discount_obj):
        try:
            category = category_discount_obj.category
            # جمع‌بندی قیمت محصولات در دسته‌بندی
            total = order_obj.items.filter(
                product__product__categories=category
            ).aggregate(total=Sum('total_price'))['total'] or 0

            discount_amount = category_discount_obj.calculate_discount(total)
            return discount_amount, category_discount_obj.discount_reason
        except Exception:
            return 0, None


    @staticmethod
    def calculate_user_discount(order_obj,user_discount_obj,total_price):
        try:
            discount_amount = user_discount_obj.calculate_discount(total_price)
            discount_reason = user_discount_obj.discount_reason
            if not discount_amount or discount_amount == 0:
                return 0, None
            return discount_amount, discount_reason
        except:
            return 0, None


    @staticmethod
    def calculate_discount_code_amount(order, discount_code, total_price):
        category_discount = CategoryUserDiscount.objects.filter(discount_code=discount_code,user=order.user, end_date__gt=timezone.now(),start_date__lte=timezone.now(), is_active=True).first()
        user_discount = UserDiscount.objects.filter(discount_code=discount_code,user=order.user, end_date__gt=timezone.now(),start_date__lte=timezone.now(), is_active=True).first()
        if category_discount:
            category_discount_amount, category_discount_reason = DiscountService.calculate_category_discount(order, category_discount)
        else:
            category_discount_amount, category_discount_reason = 0, None
        if user_discount:
            user_discount_amount, user_discount_reason = DiscountService.calculate_user_discount(order, user_discount, total_price)
        else:
            user_discount_amount, user_discount_reason = 0, None

        if category_discount_amount > user_discount_amount:
            return category_discount_amount, category_discount_reason
        else:
            return user_discount_amount, user_discount_reason











