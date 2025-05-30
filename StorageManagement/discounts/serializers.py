# discounts/serializers.py

from rest_framework import serializers
from .models import ProductDiscount, CategoryDiscount, UserDiscount

class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = [
            'id', 'name', 'description', 'discount_type', 'value',
            'start_date', 'end_date', 'is_active', 'product'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CategoryDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryDiscount
        fields = [
            'id', 'name', 'description', 'discount_type', 'value',
            'start_date', 'end_date', 'is_active', 'category'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDiscount
        fields = [
            'id', 'name', 'description', 'discount_type', 'value',
            'start_date', 'end_date', 'is_active', 'min_purchase_amount',
            'max_discount_amount'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user'] 