from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('colors',views.ColorViewSet, 'colors')
router.register('sizes',views.SizeViewSet,'sizes')
router.register('categories',views.CategoryViewSet,'categories')
router.register('categories_for_product', views.CategoriesForProductViewSet,'categories_for_product')
router.register('products', views.ProductViewSet, basename='products')


urlpattern =[

] + router.urls
