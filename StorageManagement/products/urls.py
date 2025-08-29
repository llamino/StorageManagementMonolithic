from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('colors',views.ColorViewSet, 'colors')
router.register('sizes',views.SizeViewSet,'sizes')
router.register('categories',views.CategoryViewSet,'categories')
# router.register('categories_for_product', views.CategoriesForProductViewSet,'categories_for_product')
router.register('products', views.ProductViewSet, basename='products')


urlpatterns =[
    # برای ایجاد یک نظر جدید برای یک محصول خاص.
    path('comment/<str:product_name>/', views.CommentView.as_view(),name='comment'),
    # افزودن یک محصول با تمام جزئیات مانند رنگ و سایز و قیمت و غیره
    path('create_product-property/', views.AddProductPropertyApiView.as_view(),name='create-product-property'),
] + router.urls


