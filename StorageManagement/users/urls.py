from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('address', views.AddressViewSet, basename='address')

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('edit_profile/', views.UserProfileView.as_view(), name='edit_profile'),
    path('delete_profile/', views.UserProfileView.as_view(), name='delete_profile'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshAccessTokenView.as_view(), name='refresh'),
    path('validate_jwt/', views.ValidateJWTView.as_view(), name='validate_jwt'),
] + router.urls