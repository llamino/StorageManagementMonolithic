# recommendations/urls.py
from django.urls import path
from .views import FrequentProductView, HybridRecommendationView

urlpatterns = [
    path('frequent_products/<str:product_name>/', FrequentProductView.as_view(), name='frequent_products'),
    path('recommend_related_products/<str:user_email>/', HybridRecommendationView.as_view(), name='hybrid_recommendations'),
]
