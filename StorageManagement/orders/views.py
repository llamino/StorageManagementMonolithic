# orders/views.py

from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from warehouses.models import Inventory, ProductProperty
from discounts.services import DiscountService
from django.db import transaction

class OrderViewSet(viewsets.ModelViewSet):
    """
    مدیریت سفارشات
    
    این ViewSet شامل عملیات زیر است:
    - مشاهده لیست سفارشات
    - ایجاد سفارش جدید
    - مشاهده جزئیات سفارش
    - لغو سفارش
    - پرداخت سفارش
    - ارسال سفارش
    - تحویل سفارش
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(
                user=user
            ).select_related(
                'shipping_address',
                'user'
            ).prefetch_related(
                'items__product__product',
                'items__product__size',
                'items__product__color'
            ).order_by('-created_at')
        return Order.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @swagger_auto_schema(
        operation_summary="دریافت لیست سفارشات",
        operation_description="دریافت لیست تمام سفارشات کاربر جاری",
        tags=['Orders'],
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="لیست سفارشات با موفقیت بازگردانده شد",
                schema=OrderSerializer(many=True)
            ),
            401: openapi.Response(
                description="عدم احراز هویت",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ایجاد سفارش جدید",
        operation_description="ایجاد سفارش جدید با بررسی موجودی و اعمال تخفیفات",
        tags=['Orders'],
        security=[{'Bearer': []}],
        request_body=OrderCreateSerializer,
        responses={
            201: openapi.Response(
                description="سفارش با موفقیت ایجاد شد",
                schema=OrderSerializer
            ),
            400: openapi.Response(
                description="خطا در داده‌های ورودی یا موجودی ناکافی",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(
                description="عدم احراز هویت",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data['items']

        try:
            with transaction.atomic():
                # بررسی و رزرو موجودی
                for item in items_data:
                    product = item['product']
                    quantity = item['quantity']

                    try:
                        inventory = Inventory.objects.select_for_update().get(product=product)

                        if inventory.stock < quantity:
                            return Response(
                                {
                                    'error': f'موجودی کافی برای محصول {product} وجود ندارد. موجودی فعلی: {inventory.stock}'
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        inventory.stock -= quantity
                        inventory.save()

                    except Inventory.DoesNotExist:
                        return Response(
                            {'error': f'محصول {product} در انبار موجود نیست'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # محاسبه تخفیف‌ها
                total_discount, discount_reason = DiscountService.calculate_order_discounts(items_data, request.user)

                # ایجاد سفارش
                order = serializer.save(
                    discount=total_discount,
                    discount_reason=discount_reason
                )

                # ایجاد آیتم‌های سفارش
                for item_data in items_data:
                    product = item_data['product']
                    quantity = item_data['quantity']

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        discount=item_data.get('discount', 0),
                        discount_reason=item_data.get('discount_reason')
                    )

                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'خطای غیرمنتظره در ایجاد سفارش'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="دریافت جزئیات سفارش",
        operation_description="دریافت جزئیات کامل یک سفارش خاص",
        tags=['Orders'],
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="جزئیات سفارش با موفقیت بازگردانده شد",
                schema=OrderSerializer
            ),
            404: openapi.Response(
                description="سفارش یافت نشد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(
                description="عدم احراز هویت",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="لغو سفارش",
        operation_description="لغو سفارش و بازگرداندن موجودی به انبار",
        tags=['Orders'],
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="سفارش با موفقیت لغو شد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example="سفارش با موفقیت لغو شد")
                    }
                )
            ),
            400: openapi.Response(
                description="سفارش قابل لغو نیست",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                description="سفارش یافت نشد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status not in ['pending', 'paid']:
            return Response(
                {'error': 'فقط سفارش‌های در انتظار پرداخت یا پرداخت شده قابل لغو هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # بازگرداندن آیتم‌ها به موجودی
        for item in order.items.all():
            inventory = Inventory.objects.get(product=item.product)
            inventory.stock += item.quantity
            inventory.save()

        order.status = 'canceled'
        order.save()

        return Response({'status': 'سفارش با موفقیت لغو شد'})

    @swagger_auto_schema(
        operation_summary="پرداخت سفارش",
        operation_description="انجام پرداخت برای سفارش",
        tags=['Orders'],
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="پرداخت با موفقیت انجام شد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example="پرداخت با موفقیت انجام شد")
                    }
                )
            ),
            400: openapi.Response(
                description="سفارش قابل پرداخت نیست",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                description="سفارش یافت نشد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'error': 'فقط سفارش‌های در انتظار پرداخت قابل پرداخت هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()

        return Response({'status': 'پرداخت با موفقیت انجام شد'})

    @swagger_auto_schema(
        operation_summary="ارسال سفارش",
        operation_description="ثبت ارسال سفارش با کد رهگیری",
        tags=['Orders'],
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tracking_code'],
            properties={
                'tracking_code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="کد رهگیری ارسال",
                    example="TRK123456789"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="سفارش با موفقیت ارسال شد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example="سفارش با موفقیت ارسال شد")
                    }
                )
            ),
            400: openapi.Response(
                description="سفارش قابل ارسال نیست یا کد رهگیری ارائه نشده",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                description="سفارش یافت نشد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'paid':
            return Response(
                {'error': 'فقط سفارش‌های پرداخت شده قابل ارسال هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tracking_code = request.data.get('tracking_code')
        if not tracking_code:
            return Response(
                {'error': 'کد رهگیری الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.tracking_code = tracking_code
        order.save()

        return Response({'status': 'سفارش با موفقیت ارسال شد'})

    @swagger_auto_schema(
        operation_summary="تحویل سفارش",
        operation_description="ثبت تحویل نهایی سفارش",
        tags=['Orders'],
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="سفارش با موفقیت تحویل داده شد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, example="سفارش با موفقیت تحویل داده شد")
                    }
                )
            ),
            400: openapi.Response(
                description="سفارش قابل تحویل نیست",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                description="سفارش یافت نشد",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'shipped':
            return Response(
                {'error': 'فقط سفارش‌های ارسال شده قابل تحویل هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'delivered'
        order.save()

        return Response({'status': 'سفارش با موفقیت تحویل داده شد'})