# orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem
from users.serializers import AddressSerializer
from products.serializers import ProductPropertySerializer
from users.models import Address

# ===================================================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'order', 'product', 'quantity', 'price',
            'discount_amount', 'discount_reason', 'total_price'
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'status', 'payment_method', 'shipping_address',
            'total_price', 'final_price', 'tax', 'shipping_price',
            'discount_amount', 'discount_reason', 'discount_code',
            'created_at', 'paid_at', 'shipped_at', 'tracking_code', 'notes',
            'items'
        )
        read_only_fields = ('total_price', 'final_price', 'discount_amount', 'discount_reason', 'created_at')
