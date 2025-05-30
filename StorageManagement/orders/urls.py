# orders/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from orders.autocompletes import AddressAutocomplete
router = DefaultRouter()
router.register('', views.OrderViewSet, basename='orders') 

urlpatterns = [
    path('', include(router.urls)),
    path('admin-autocomplete/address/', AddressAutocomplete.as_view(), name='address-autocomplete'),

]
