# recommendations/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from recommendations.models import RuleProduct
from recommendations.serializers import ProductRecommendationSerializer
from products.models import Product
from drf_yasg.utils import swagger_auto_schema


class FrequentProductView(APIView):
    @swagger_auto_schema(
        tags=['recommendations'],
        operation_description='this endpoint will return products that mostly bought with current product.',
        request_body=ProductRecommendationSerializer)

    def get(self, request, product_name):
        # Get rules where the product is an antecedent

        if not Product.objects.filter(name=product_name).exists():
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        antecedent_rules = RuleProduct.objects.filter(
            product__name=product_name,
            is_antecedent=True
        ).values_list('rule_id', flat=True)

        if not antecedent_rules:
            return Response(
                {"detail": "No rules found for this product."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get consequent products in these rules
        consequents = RuleProduct.objects.filter(
            rule_id__in=antecedent_rules,
            is_antecedent=False
        ).select_related('rule', 'product').distinct()

        if not consequents.exists():
            return Response(
                {"detail": "No recommendations found for this product."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductRecommendationSerializer(consequents, many=True)
        return Response(serializer.data)
