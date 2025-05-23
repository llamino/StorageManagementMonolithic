from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path
router = DefaultRouter()
router.register('sizes', views.SizeSupplierViewSet, basename='sizes')
router.register('colors', views.ColorSupplierViewSet, basename='colors')
router.register('suppliers', views.SupplierViewSet, basename='suppliers')
router.register('categories', views.CategorySupplierViewSet, basename='categories')
router.register('products', views.ProductDetailSupplierViewSet, basename='products')
router.register('inventory', views.InventorySupplierViewSet, basename='inventory')
urlpatterns = [

] + router.urls
