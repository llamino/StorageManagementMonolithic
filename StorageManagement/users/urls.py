from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('address', views.AddressViewSet, basename='address')

urlpatterns = [
    path('profile/', views.UserProfielView.as_view(), name='profile'),
    path('create_profile/', views.UserProfielView.as_view(), name='create_profile'),
    path('edit_profile/', views.UserProfielView.as_view(), name='edit_profile'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', views.RefreshAccessTokenView.as_view(), name='refresh'),
    path('validate_jwt/', views.ValidateJWTView.as_view(), name='validate_jwt'),
] + router.urls