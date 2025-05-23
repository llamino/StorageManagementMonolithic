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
from .serializers import ProfileSerializer,LoginSerializer, UserProfileSerializer, AddressSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    tags=['Addresses'],
    operation_description="API endpoints for managing user addresses",
    security=[{'Bearer': []}]

)
class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user addresses.

    Provides CRUD operations for Address objects.
    Only authenticated users can access their own addresses.
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_description="Get all addresses for the authenticated user",
        responses={200: AddressSerializer(many=True)},
        security=[{'Bearer': []}]

    )
    def get_queryset(self):
        """
        Get all addresses for the authenticated user.

        Returns only the addresses belonging to the authenticated user.
        For Swagger schema generation, returns an empty queryset.

        Original Persian comment:
        # بررسی اینکه آیا درخواست برای تولید اسکیما است یا خیر
        """
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()

        user = self.request.user
        if user.is_authenticated:
            return user.addresses.all()
        return Address.objects.none()

    @swagger_auto_schema(
        operation_description="Create a new address for the authenticated user",
        request_body=AddressSerializer,
        responses={201: AddressSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new address for the authenticated user.

        The user is automatically added to the address.

        Original Persian comment:
        # اضافه کردن context
        # user به صورت خودکار اضافه می‌شود
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})  # اضافه کردن context
        serializer.is_valid(raise_exception=True)
        serializer.save()  # user به صورت خودکار اضافه می‌شود
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="List all addresses for the authenticated user",
        responses={200: AddressSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """
        List all addresses for the authenticated user.

        Returns a paginated list of addresses if pagination is enabled.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific address for the authenticated user",
        responses={200: AddressSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific address for the authenticated user.

        Original Persian comment:
        # فقط یک شیء را دریافت می‌کند
        """
        instance = self.get_object()  # فقط یک شیء را دریافت می‌کند
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Partially update a specific address for the authenticated user",
        request_body=AddressSerializer,
        responses={200: AddressSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a specific address for the authenticated user.

        Original Persian comment:
        # فقط یک شیء را به‌روزرسانی می‌کند
        """
        instance = self.get_object()  # فقط یک شیء را به‌روزرسانی می‌کند
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Fully update a specific address for the authenticated user",
        request_body=AddressSerializer,
        responses={200: AddressSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """
        Fully update a specific address for the authenticated user.

        Original Persian comment:
        # فقط یک شیء را به‌روزرسانی می‌کند
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # فقط یک شیء را به‌روزرسانی می‌کند
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific address for the authenticated user",
        responses={204: "No content - address deleted successfully"}
    )
    def destroy(self, request, pk=None):
        """
        Delete a specific address for the authenticated user.
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    tags=['UserProfile'],
    operation_description="API endpoints for managing user profile",
)
class UserProfileView(APIView):
    """
    View for managing user profile.

    Provides operations to get, update, and delete user profile.
    Only authenticated users can access their own profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    @swagger_auto_schema(
        operation_description="Get the authenticated user's profile",
        responses={200: UserProfileSerializer()}
    )
    def get(self, request):
        """
        Get the authenticated user's profile.
        """
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Fully update the authenticated user's profile",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer()}
    )
    def put(self, request):
        """
        Fully update the authenticated user's profile.

        Handles form-data format for profile updates.

        Original Persian comment:
        # این تغییر ساختار به این دلیل است که در postman داده ها را به صورت form-data ارسال میکنم. اگر قرار بود به صورت json ارسال کنم، نیاز نبود که به این شکل تغییر ساختار بدهم
        # حذف 'profile[' و ']' از کلیدها
        # حذف کلیدهای مربوط به پروفایل از دیکشنری اصلی
        # اضافه کردن دیکشنری پروفایل به دیکشنری اصلی
        """
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

    @swagger_auto_schema(
        operation_description="Partially update the authenticated user's profile",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer()}
    )
    def patch(self, request):
        """
        Partially update the authenticated user's profile.
        """
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Deactivate the authenticated user's account",
        responses={
            204: openapi.Response(
                description="No content - user deactivated successfully",
                examples={"application/json": {"detail": "User deactivated successfully."}}
            )
        }
    )
    def delete(self, request, *args, **kwargs):
        """
        Deactivate the authenticated user's account.

        Note: This doesn't actually delete the user, but sets is_active to False.
        """
        user = request.user
        user.is_active = False
        user.save()
        return Response({"detail": "User deactivated successfully."}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    tags=['Register'],
    operation_description="API endpoint for user registration",
)
class RegisterView(APIView):
    """
    View for user registration.

    Provides operation to register a new user.
    """
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Created - user registered successfully",
                examples={"application/json": {"message": "User created successfully"}}
            ),
            400: "Bad request - invalid data",
            500: "Internal server error"
        }
    )
    def post(self, request):
        """
        Register a new user.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"New user registered: {user.email}")
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error saving user: {e}")
                return Response({'error': 'An error occurred while creating the user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning(f"Invalid registration data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    tags=['Authentication'],
    operation_description="API endpoint for user login",
)
class LoginView(APIView):
    """
    View for user login.

    Provides operation to authenticate a user and get JWT tokens.
    """

    @swagger_auto_schema(
        operation_description="Login with email and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="OK - login successful",
                examples={"application/json": {
                    "access": "access_token_example",
                    "refresh": "refresh_token_example"
                }}
            ),
            400: "Bad request - invalid data",
            401: "Unauthorized - invalid credentials",
            500: "Internal server error"
        }
    )
    def post(self, request):
        """
        Login with email and password.

        Returns JWT access and refresh tokens on successful authentication.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

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


@swagger_auto_schema(
    tags=['Authentication'],
    operation_description="API endpoint for refreshing access token",
)
class RefreshAccessTokenView(APIView):
    """
    View for refreshing access token.

    Provides operation to get a new access token using a refresh token.
    """

    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            }
        ),
        responses={
            200: openapi.Response(
                description="OK - token refreshed successfully",
                examples={"application/json": {"access": "new_access_token_example"}}
            ),
            400: "Bad request - refresh token not provided",
            401: "Unauthorized - invalid refresh token",
            500: "Internal server error"
        }
    )
    def post(self, request):
        """
        Refresh access token using refresh token.

        Returns a new access token on successful validation of the refresh token.
        """
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


@swagger_auto_schema(
    tags=['Authentication'],
    operation_description="API endpoint for user logout",
)
class LogoutView(APIView):
    """
    View for user logout.

    Provides operation to blacklist a refresh token, effectively logging out the user.
    Only authenticated users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    @swagger_auto_schema(
        operation_description="Logout by blacklisting the refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist')
            }
        ),
        responses={
            200: openapi.Response(
                description="OK - logout successful",
                examples={"application/json": {"msg": "Successfully logged out"}}
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "msg": "Refresh token is required"
                    }
                }
            )
        }
    )
    def post(self, request):
        """
        Logout by blacklisting the refresh token.

        Blacklists the provided refresh token, effectively logging out the user.
        """
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


@swagger_auto_schema(
    tags=['Authentication'],
    operation_description="API endpoint for validating JWT token",
)
class ValidateJWTView(APIView):
    """
    View for validating JWT token.

    Provides operation to validate if a JWT token is valid.
    Only authenticated users can access this endpoint.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Validate JWT token",
        responses={
            200: openapi.Response(
                description="OK - token is valid",
                examples={"application/json": {"message": "Token is valid"}}
            ),
            401: "Unauthorized - invalid token",
            500: "Internal server error"
        }
    )
    def get(self, request):
        """
        Validate JWT token.

        Returns a success message if the token is valid.
        """
        try:
            logger.info(f"JWT validated for user: {request.user.username}")
            return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
