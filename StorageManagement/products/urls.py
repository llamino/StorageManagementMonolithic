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
    path('create_comment/<str:product_name>/', views.CommentView.as_view(),'create-comment'),
    # برای حذف یک نظر خاص که توسط کاربر ایجاد شده است.
    path('delete_comment/<str:product_name>/', views.CommentView.as_view(),'delete-comment'),
    # برای دریافت لیست نظرات مربوط به یک محصول خاص.
    path('get_comment/<str:product_name>/',views.CommentView.as_view(),'get-list-comment')
] + router.urls
