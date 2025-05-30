 # discount/services.py

from django.utils import timezone
from discounts.models import ProductDiscount, CategoryDiscount, UserDiscount
from products.models import ProductProperty

class DiscountService:
    @staticmethod
    def get_active_discounts():
        now = timezone.now()
        return {
            'product_discounts': ProductDiscount.objects.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            ),
            'category_discounts': CategoryDiscount.objects.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            ),
            'user_discounts': UserDiscount.objects.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            )
        }

    @staticmethod
    def calculate_product_discount(product_property, price):
        discounts = ProductDiscount.objects.filter(
            product=product_property.product,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        if not discounts.exists():
            return 0, None

        # رفع مشکل max() روی queryset خالی
        discount_amounts = [(d.calculate_discount(price), d) for d in discounts]
        if not discount_amounts:
            return 0, None

        best_amount, best_discount = max(discount_amounts, key=lambda x: x[0])
        return best_amount, f"تخفیف محصول: {best_discount.name}"

    @staticmethod
    def calculate_category_discount(product_property, price):
        category_discounts = CategoryDiscount.objects.filter(
            category__in=product_property.product.categories.all(),
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        if not category_discounts.exists():
            return 0, None

        # رفع مشکل max() روی queryset خالی
        discount_amounts = [(d.calculate_discount(price), d) for d in category_discounts]
        if not discount_amounts:
            return 0, None

        best_amount, best_discount = max(discount_amounts, key=lambda x: x[0])
        return best_amount, f"تخفیف دسته‌بندی: {best_discount.name}"

    @staticmethod
    def calculate_user_discount(user, total_price):
        user_discounts = UserDiscount.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        if not user_discounts.exists():
            return 0, None

        # رفع مشکل max() روی queryset خالی
        discount_amounts = [(d.calculate_discount(total_price), d) for d in user_discounts]
        if not discount_amounts:
            return 0, None

        best_amount, best_discount = max(discount_amounts, key=lambda x: x[0])
        return best_amount, f"تخفیف کاربر: {best_discount.name}"

    @classmethod
    def calculate_order_discounts(cls, order_items, user):
        total_discount = 0
        discount_reasons = []

        # Calculate product and category discounts for each item
        for item in order_items:
            product_property = item['product']
            quantity = item['quantity']
            price = product_property.price * quantity

            # Calculate product discount
            product_discount, product_reason = cls.calculate_product_discount(product_property, price)
            
            # Calculate category discount
            category_discount, category_reason = cls.calculate_category_discount(product_property, price)

            # Apply the higher discount
            if product_discount > category_discount:
                item['discount'] = product_discount
                item['discount_reason'] = product_reason
                total_discount += product_discount
                if product_reason:
                    discount_reasons.append(product_reason)
            else:
                item['discount'] = category_discount
                item['discount_reason'] = category_reason
                total_discount += category_discount
                if category_reason:
                    discount_reasons.append(category_reason)

        # Calculate user discount on total price
        total_price = sum(item['product'].price * item['quantity'] for item in order_items)
        user_discount, user_reason = cls.calculate_user_discount(user, total_price)

        if user_discount > 0:
            total_discount += user_discount
            if user_reason:
                discount_reasons.append(user_reason)

        return total_discount, ' | '.join(discount_reasons) if discount_reasons else None 