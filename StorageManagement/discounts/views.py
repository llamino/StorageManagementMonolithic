# discounts/views.py

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ProductDiscount, CategoryDiscount, UserDiscount
from .serializers import (
    ProductDiscountSerializer,
    CategoryDiscountSerializer,
    UserDiscountSerializer
)

# Create your views here.

class ProductDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductDiscountSerializer
    queryset = ProductDiscount.objects.filter(is_active=True)

    @swagger_auto_schema(
        tags=['discounts'],
        operation_description="دریافت لیست تخفیف‌های محصول",
        responses={
            200: ProductDiscountSerializer(many=True),
            401: "عدم احراز هویت"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['discounts'],
        operation_description="ایجاد تخفیف جدید برای محصول",
        request_body=ProductDiscountSerializer,
        responses={
            201: ProductDiscountSerializer,
            400: "خطا در داده‌های ورودی",
            401: "عدم احراز هویت"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class CategoryDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryDiscountSerializer
    queryset = CategoryDiscount.objects.filter(is_active=True)

    @swagger_auto_schema(
        tags=['discounts'],
        operation_description="دریافت لیست تخفیف‌های دسته‌بندی",
        responses={
            200: CategoryDiscountSerializer(many=True),
            401: "عدم احراز هویت"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['discounts'],
        operation_description="ایجاد تخفیف جدید برای دسته‌بندی",
        request_body=CategoryDiscountSerializer,
        responses={
            201: CategoryDiscountSerializer,
            400: "خطا در داده‌های ورودی",
            401: "عدم احراز هویت"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class UserDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDiscountSerializer
    queryset = UserDiscount.objects.filter(is_active=True)

    def get_queryset(self):
        return UserDiscount.objects.filter(
            user=self.request.user,
            is_active=True
        )

    @swagger_auto_schema(
        tags=['discounts'],
        operation_description="دریافت لیست تخفیف‌های کاربر",
        responses={
            200: UserDiscountSerializer(many=True),
            401: "عدم احراز هویت"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['discounts'],
        operation_description="ایجاد تخفیف جدید برای کاربر",
        request_body=UserDiscountSerializer,
        responses={
            201: UserDiscountSerializer,
            400: "خطا در داده‌های ورودی",
            401: "عدم احراز هویت"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
