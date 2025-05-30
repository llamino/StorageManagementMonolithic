# recommendations/serializers.py
from rest_framework import serializers
from products.models import Product
from recommendations.models import RuleProduct


class ProductRecommendationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.ImageField(source='product.image')
    product_avg_score = serializers.FloatField(source='product.avg_score')

    class Meta:
        model = RuleProduct
        fields = [
            'product_name',
            'product_image',
            'product_avg_score',
            'confidence',
            'support',
            'lift'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # ساختاردهی مجدد خروجی
        return {
            'product': {
                'name': data['product_name'],
                'image': data['product_image'],
                'avg_score': data['product_avg_score']
            },
            'confidence': instance.rule.confidence,
            'support': instance.rule.support,
            'lift': instance.rule.lift
        }