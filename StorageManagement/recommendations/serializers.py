# recommendations/serializers.py
from rest_framework import serializers
from products.models import Product
from recommendations.models import RuleProduct


class ProductRecommendationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.ImageField(source='product.image')
    product_avg_score = serializers.FloatField(source='product.avg_score')
    confidence = serializers.SerializerMethodField()
    support = serializers.SerializerMethodField()
    lift = serializers.SerializerMethodField()

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

    def get_confidence(self, obj):
        return obj.rule.confidence

    def get_support(self, obj):
        return obj.rule.support

    def get_lift(self, obj):
        return obj.rule.lift

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'product': {
                'name': data['product_name'],
                'image': data['product_image'],
                'avg_score': data['product_avg_score']
            },
            'confidence': data['confidence'],
            'support': data['support'],
            'lift': data['lift']
        }


class HybridRecommendationSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    product_image = serializers.ImageField()
    product_avg_score = serializers.FloatField()
    score = serializers.FloatField()
    source = serializers.CharField()