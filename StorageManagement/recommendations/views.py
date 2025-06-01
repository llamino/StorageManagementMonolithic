# recommendations/views.py
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from recommendations.models import RuleProduct, UserRecommendation
from recommendations.serializers import ProductRecommendationSerializer, HybridRecommendationSerializer
from products.models import Product
from drf_yasg.utils import swagger_auto_schema
from recommendations.algorithms.product_recommendation import HybridRecommender
from users.models import User
from datetime import timedelta
from drf_yasg import openapi
from django.db.models import Max

@swagger_auto_schema(
    tags=['recommendations'],
)
class FrequentProductView(APIView):
    @swagger_auto_schema(
        tags=['recommendations'],
        operation_description='this endpoint will return products that mostly bought with current product.',
        manual_parameters=[
            openapi.Parameter(
                'product_name',
                openapi.IN_PATH,
                description="Name of the product",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request, product_name):
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

        # Get distinct consequent products with best metrics
        consequents = (
            RuleProduct.objects.filter(
                rule_id__in=antecedent_rules,
                is_antecedent=False
            )
            .values('product__name')  # Group by product name (primary key)
            .annotate(
                best_lift=Max('rule__lift'),
                best_confidence=Max('rule__confidence'),
                best_support=Max('rule__support')
            )
            .order_by('-best_lift')
        )

        # Get product details in a single query
        product_names = [c['product__name'] for c in consequents]
        products = Product.objects.filter(name__in=product_names)
        product_map = {p.name: p for p in products}

        # Build response
        result = []
        for c in consequents:
            product_name = c['product__name']
            product = product_map.get(product_name)
            if product:
                result.append({
                    "product": {
                        "name": product.name,
                        "image": request.build_absolute_uri(product.image.url) if product.image else None,
                        "avg_score": product.avg_score
                    },
                    "confidence": c['best_confidence'],
                    "support": c['best_support'],
                    "lift": c['best_lift']
                })
        return Response(result)


user_email_param = openapi.Parameter(
    'user_email', openapi.IN_PATH,
    description="Email of the user", type=openapi.TYPE_STRING
)

@swagger_auto_schema(
    tags=['recommendations'],
    manual_parameters=[user_email_param],
    operation_description='Get personalized product recommendations using hybrid approach',
    responses={
        200: 'Successfully retrieved recommendations',
        400: 'Invalid user email',
        404: 'User not found',
        500: 'Internal server error'
    }
)
class HybridRecommendationView(APIView):
    @swagger_auto_schema(
        tags=['recommendations'],
        operation_description='Get personalized product recommendations using hybrid approach',
        responses={
            200: 'Successfully retrieved recommendations',
            400: 'Invalid user email',
            404: 'User not found',
            500: 'Internal server error'
        }
    )
    def get(self, request, user_email):
        try:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            recommendation_data = UserRecommendation.objects.filter(user=user).first()

            if recommendation_data and timezone.now() - recommendation_data.updated_at < timedelta(days=7):
                serializer = HybridRecommendationSerializer(recommendation_data.data['recommendations'], many=True)
                return Response({
                    'recommendations': serializer.data,
                    'metadata': recommendation_data.data.get('metadata', {})
                }, status=status.HTTP_200_OK)

            recommender = HybridRecommender()
            result = recommender.get_hybrid_recommendations(user_email=user_email)

            if not result['success']:
                return Response({"detail": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # ذخیره در دیتابیس
            UserRecommendation.objects.update_or_create(
                user=user,
                defaults={'data': result, 'updated_at': timezone.now()}
            )

            serializer = HybridRecommendationSerializer(result['recommendations'], many=True)
            return Response({
                'recommendations': serializer.data,
                'metadata': result.get('metadata', {})
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)