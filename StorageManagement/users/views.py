import json
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import Profile, Address, User
from .serializers import ProfileSerializer, UserProfileSerializer, AddressSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
logger = logging.getLogger(__name__)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        user = self.request.user
        return user.addresses.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})  # اضافه کردن context
        serializer.is_valid(raise_exception=True)
        serializer.save()  # user به صورت خودکار اضافه می‌شود
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # فقط یک شیء را دریافت می‌کند
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()  # فقط یک شیء را به‌روزرسانی می‌کند
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # فقط یک شیء را به‌روزرسانی می‌کند
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data
        profile_data = {}
        # این تغییر ساختار به این دلیل است که در postman داده ها را به صورت form-data ارسال میکنم. اگر قرار بود به صورت json ارسال کنم، نیاز نبود که به این شکل تغییر ساختار بدهم
        for key, value in data.items():
            if key.startswith('profile[') and key.endswith(']'):
                # حذف 'profile[' و ']' از کلیدها
                profile_key = key[8:-1]
                profile_data[profile_key] = value[0] if isinstance(value, list) else value
        # حذف کلیدهای مربوط به پروفایل از دیکشنری اصلی
        data = {k: v for k, v in data.items() if not k.startswith('profile[')}
        # اضافه کردن دیکشنری پروفایل به دیکشنری اصلی
        data['profile'] = profile_data

        serializer = self.serializer_class(user, data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"detail": "User deactivated successfully."}, status=status.HTTP_204_NO_CONTENT)
class RegisterView(APIView):
    serializer_class = RegisterSerializer
    def post(self, request):
        print('amin ahmadi 1')
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            print('amin ahmadi 2')
            try:
                user = serializer.save()
                print('amin ahmadi 3')
                # logger.info(f"New user registered: {user.username}")
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error saving user: {e}")
                return Response({'error': 'An error occurred while creating the user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning(f"Invalid registration data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            print(User.objects.filter(email=email).exists())
            # print(user.password)
        except:
            raise AuthenticationFailed({'error': 'amin ahmadi'})
        try:
            user = authenticate(request, username=email, password=password)
            if not user:
                logger.warning(f"Failed login attempt for email: {email}")

                raise AuthenticationFailed('Invalid credentials')

            refresh = RefreshToken.for_user(user)
            logger.info(f"User logged in: {email}")
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            logger.warning(f"Authentication failed for email: {email} - {e}")
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:

            logger.error(f"Unexpected error during login: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RefreshAccessTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({'access': new_access_token}, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.warning(f"Invalid refresh token: {e}")
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Unexpected error while refreshing token: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            logger.warning("Logout attempted without providing a refresh token.")
            return JsonResponse({"msg": "Refresh token is required"}, status=400)

        try:
            # Attempt to blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"User {request.user.email} successfully logged out.")
            return JsonResponse({"msg": "Successfully logged out"}, status=200)
        except TokenError:
            logger.warning(f"Invalid or already blacklisted token provided by user {request.user.email}.")
            return JsonResponse({"msg": "Token is invalid or already blacklisted"}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error during logout for user {request.user.email}: {str(e)}")
            return JsonResponse({"msg": "Failed to log out", "error": str(e)}, status=400)

class ValidateJWTView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logger.info(f"JWT validated for user: {request.user.username}")
            return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
