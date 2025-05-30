# orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem
from users.serializers import AddressSerializer
from products.serializers import ProductPropertySerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductPropertySerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price', 'discount', 'total_price']
        read_only_fields = ['id', 'total_price']

    def validate(self, data):
        product = data['product']
        if not product.can_sale:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('این محصول فروشی نیست')

        if data['quantity'] <= 0:
            raise ValueError('تعداد باید بیشتر از صفر باشد')

        return data
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'status_display', 'payment_method', 'payment_method_display',
            'shipping_address', 'total_price', 'discount', 'tax', 'shipping_price', 'final_price',
            'created_at', 'paid_at', 'shipped_at', 'tracking_code', 'notes', 'items'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'paid_at', 'shipped_at', 'final_price']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError({"user": "User must be authenticated."})
        
        validated_data['user'] = request.user
        order = Order.objects.create(**validated_data)
        return order


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'shipping_address_id', 'payment_method', 'items', 'notes'
        ]

    def validate_shipping_address_id(self, value):
        """بررسی صحت آدرس و تعلق آن به کاربر"""
        from users.models import Address
        request = self.context.get('request')
        if not Address.objects.filter(id=value, user=request.user).exists():
            raise serializers.ValidationError("آدرس انتخابی نامعتبر یا متعلق به شما نیست")
        return value

    def validate_items(self, value):
        """بررسی صحت آیتم‌های سفارش"""
        if not value:
            raise serializers.ValidationError("حداقل یک محصول باید انتخاب شود")

        for item in value:
            if item['quantity'] <= 0:
                raise serializers.ValidationError("تعداد محصول باید بیشتر از صفر باشد")

            if not item['product'].can_sale:
                raise serializers.ValidationError(f"محصول {item['product']} قابل فروش نیست")

        return value


    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError({"user": "User must be authenticated."})

        items_data = validated_data.pop('items')
        shipping_address_id = validated_data.pop('shipping_address_id')

        # Calculate total price
        total_price = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            price = product.price
            total_price += price * quantity

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address_id=shipping_address_id,
            total_price=total_price,
            **validated_data
        )

        # Create order items
        for item_data in items_data:
            product = item_data['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price,  # قیمت از سمت سرور
                discount=item_data.get('discount', 0),
                discount_reason=item_data.get('discount_reason')
            )

        return order
