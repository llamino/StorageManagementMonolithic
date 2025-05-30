# recommendations/urls.py
from django.urls import path
from .views import FrequentProductView

urlpatterns = [
    path('frequent_products/<str:product_name>/', FrequentProductView.as_view(), name='frequent_products'),
    path('recommend_related_products/<int:user_id>/')
]
