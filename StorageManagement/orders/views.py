# orders/views.py
from collections import defaultdict

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from discounts.services import DiscountService
from products.models import ProductProperty
from users.models import Address, User
from .models import Order, OrderItem
from orders.serializers import OrderItemSerializer, OrderSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

class ListOrderItemView(APIView):
    @swagger_auto_schema(
        tags=['orders'],
        operation_description='نمایش اطلاعات یک سفارش به‌همراه آیتم‌های آن',
        responses={
            200: OrderSerializer,
            404: "سفارش یافت نشد"
        }
    )
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CancelOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['orders'],
        operation_description='لغو سفارش',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['order_id'],
            properties={
                'order_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='شناسه سفارش')
            }
        ),
        responses={
            200: OrderSerializer,
            404: "سفارش یافت نشد"
        }
    )
    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'detail': 'پارامتر order_id ارسال نشده است.'}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id=order_id)
        if order.status == 'canceled':
            return Response({'detail': 'order already has canceled'}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == 'paid' or order.status == 'shipped' or order.status == 'delivered':
            return Response({'detail': 'this order can not canceled'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'canceled'
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)
class CreateOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['orders'],
        operation_description='create order',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['shipping_address_id', 'items'],
            properties={
                'shipping_address_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'payment_method_id': openapi.Schema(type=openapi.TYPE_STRING, enum=['online', 'cash', 'wallet']),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                'discount_code': openapi.Schema(type=openapi.TYPE_STRING),
                'items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'product_property_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                        required=['product_property_id', 'quantity']
                    )
                ),
            }
        )
    )
    def post(self, request):
        user_id = request.data.get('user_id') or request.user.id

        if not request.user.is_staff and user_id != request.user.id:
            return Response(
                {'error': 'شما اجازه ایجاد سفارش برای کاربر دیگری را ندارید'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        shipping_address_id = data.get('shipping_address_id')
        payment_method = data.get('payment_method_id', 'online')
        discount_code = data.get('discount_code')
        items_data = data.get('items')

        if not shipping_address_id or not items_data:
            return Response({'error': 'اطلاعات ناقص است.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_payment_methods = dict(Order.PAYMENT_METHOD_CHOICES).keys()
        if payment_method not in valid_payment_methods:
            return Response({'error': 'روش پرداخت نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=user_id)
        except Address.DoesNotExist:
            return Response({'error': 'آدرس یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(items_data, list):
            return Response({'error': 'قالب آیتم‌ها نادرست است'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validated_items = []
            for item in items_data:
                product_property_id = int(item['product_property_id'])
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise ValueError('تعداد باید بزرگتر از صفر باشد')
                validated_items.append({'product_property_id': product_property_id, 'quantity': quantity})
        except (KeyError, TypeError, ValueError):
            return Response({'error': 'مقادیر product_property_id و quantity باید اعداد صحیح مثبت باشند'}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        order = None

        try:
            with transaction.atomic():
                product_quantities = defaultdict(int)
                property_ids = set()

                for item in validated_items:
                    pid = item['product_property_id']
                    qty = item['quantity']
                    product_quantities[pid] += qty
                    property_ids.add(pid)

                products = ProductProperty.objects.filter(
                    id__in=property_ids
                ).select_for_update()

                product_map = {p.id: p for p in products}

                for pid, total_quantity in product_quantities.items():
                    if pid not in product_map:
                        errors.append(f"ویژگی محصول با شناسه {pid} یافت نشد")
                        continue

                    product = product_map[pid]
                    if product.total_stock < total_quantity:
                        errors.append(
                            f"موجودی محصول '{product}' کافی نیست (موجودی: {product.total_stock}, درخواستی: {total_quantity})")

                if errors:
                    return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

                for pid, total_quantity in product_quantities.items():
                    product = product_map[pid]
                    product.total_stock -= total_quantity
                    product.save()

                order = Order.objects.create(
                    user=user,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    status='pending',
                    discount_code=discount_code,
                    total_price=0,
                    final_price=0,
                )

                for item in validated_items:
                    pid = item['product_property_id']
                    product = product_map[pid]
                    order_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                        price=product.sell_price,
                    )
                    order_item.save()

                order.total_price = order.calculate_total_price()
                order.final_price = order.calculate_final_price()
                order.save()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            if order and order.id:
                order.delete()
            return Response({'error': f'خطا در ایجاد سفارش: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateOrderStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # اگر فقط ادمین دسترسی داشته باشه: [IsAdminUser]

    @swagger_auto_schema(
        tags=['orders'],
        operation_description='به‌روزرسانی وضعیت سفارش (فقط برای ادمین)',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['order_id', 'status'],
            properties={
                'order_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[c[0] for c in Order.STATUS_CHOICES]
                ),
            }
        ),
        responses={
            200: OrderSerializer,
            400: 'وضعیت نامعتبر',
            403: 'دسترسی غیرمجاز',
            404: 'سفارش یافت نشد'
        }
    )
    def post(self, request):
        # بررسی دسترسی
        if not request.user.is_staff:
            return Response(
                {'detail': 'فقط ادمین می‌تواند وضعیت سفارش را تغییر دهد'},
                status=status.HTTP_403_FORBIDDEN
            )

        # گرفتن داده‌ها
        order_id = request.data.get('order_id')
        status_val = request.data.get('status')

        # بررسی معتبر بودن وضعیت
        if status_val not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'وضعیت نامعتبر'}, status=status.HTTP_400_BAD_REQUEST)

        # پیدا کردن سفارش
        order = get_object_or_404(Order, id=order_id)

        # آپدیت وضعیت
        order.status = status_val
        if status_val == 'paid':
            order.paid_at = timezone.now()
        elif status_val == 'shipped':
            order.shipped_at = timezone.now()
        order.save()

        # سریالایز و خروجی
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListUserOrdersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['orders'],
        operation_description='نمایش همه سفارش‌های کاربر جاری',
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateInvoicePdfView(APIView):
    pass
# class OrderViewSet(viewsets.ModelViewSet):
#     """
#     مدیریت سفارشات
#
#     این ViewSet شامل عملیات زیر است:
#     - مشاهده لیست سفارشات
#     - ایجاد سفارش جدید
#     - مشاهده جزئیات سفارش
#     - لغو سفارش
#     - پرداخت سفارش
#     - ارسال سفارش
#     - تحویل سفارش
#     """
#
#     permission_classes = [IsAuthenticated]
#     serializer_class = OrderSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated:
#             return Order.objects.filter(
#                 user=user
#             ).select_related(
#                 'shipping_address',
#                 'user'
#             ).prefetch_related(
#                 'items__product__product',
#                 'items__product__size',
#                 'items__product__color'
#             ).order_by('-created_at')
#         return Order.objects.none()
#
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return OrderCreateSerializer
#         return OrderSerializer
#
#     @swagger_auto_schema(
#         operation_summary="دریافت لیست سفارشات",
#         operation_description="دریافت لیست تمام سفارشات کاربر جاری",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         responses={
#             200: openapi.Response(
#                 description="لیست سفارشات با موفقیت بازگردانده شد",
#                 schema=OrderSerializer(many=True)
#             ),
#             401: openapi.Response(
#                 description="عدم احراز هویت",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
#
#     @swagger_auto_schema(
#         operation_summary="ایجاد سفارش جدید",
#         operation_description="ایجاد سفارش جدید با بررسی موجودی و اعمال تخفیفات",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         request_body=OrderCreateSerializer,
#         responses={
#             201: openapi.Response(
#                 description="سفارش با موفقیت ایجاد شد",
#                 schema=OrderSerializer
#             ),
#             400: openapi.Response(
#                 description="خطا در داده‌های ورودی یا موجودی ناکافی",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'error': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             ),
#             401: openapi.Response(
#                 description="عدم احراز هویت",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         items_data = serializer.validated_data['items']
#
#         try:
#             with transaction.atomic():
#                 # بررسی و رزرو موجودی
#                 for item in items_data:
#                     product = item['product']
#                     quantity = item['quantity']
#
#                     try:
#                         inventory = Inventory.objects.select_for_update().get(product=product)
#
#                         if inventory.stock < quantity:
#                             return Response(
#                                 {
#                                     'error': f'موجودی کافی برای محصول {product} وجود ندارد. موجودی فعلی: {inventory.stock}'
#                                 },
#                                 status=status.HTTP_400_BAD_REQUEST
#                             )
#
#                         inventory.stock -= quantity
#                         inventory.save()
#
#                     except Inventory.DoesNotExist:
#                         return Response(
#                             {'error': f'محصول {product} در انبار موجود نیست'},
#                             status=status.HTTP_400_BAD_REQUEST
#                         )
#
#                 # محاسبه تخفیف‌ها
#                 total_discount, discount_reason = DiscountService.calculate_order_discounts(items_data, request.user)
#
#                 # ایجاد سفارش
#                 order = serializer.save(
#                     discount=total_discount,
#                     discount_reason=discount_reason
#                 )
#
#                 # ایجاد آیتم‌های سفارش
#                 for item_data in items_data:
#                     product = item_data['product']
#                     quantity = item_data['quantity']
#
#                     OrderItem.objects.create(
#                         order=order,
#                         product=product,
#                         quantity=quantity,
#                         price=product.price,
#                         discount=item_data.get('discount', 0),
#                         discount_reason=item_data.get('discount_reason')
#                     )
#
#                 return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
#
#         except ValidationError as e:
#             return Response(
#                 {'error': str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             return Response(
#                 {'error': 'خطای غیرمنتظره در ایجاد سفارش'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#
#     @swagger_auto_schema(
#         operation_summary="دریافت جزئیات سفارش",
#         operation_description="دریافت جزئیات کامل یک سفارش خاص",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         responses={
#             200: openapi.Response(
#                 description="جزئیات سفارش با موفقیت بازگردانده شد",
#                 schema=OrderSerializer
#             ),
#             404: openapi.Response(
#                 description="سفارش یافت نشد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             ),
#             401: openapi.Response(
#                 description="عدم احراز هویت",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     def retrieve(self, request, *args, **kwargs):
#         return super().retrieve(request, *args, **kwargs)
#
#     @swagger_auto_schema(
#         operation_summary="لغو سفارش",
#         operation_description="لغو سفارش و بازگرداندن موجودی به انبار",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         responses={
#             200: openapi.Response(
#                 description="سفارش با موفقیت لغو شد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'status': openapi.Schema(type=openapi.TYPE_STRING, example="سفارش با موفقیت لغو شد")
#                     }
#                 )
#             ),
#             400: openapi.Response(
#                 description="سفارش قابل لغو نیست",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'error': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             ),
#             404: openapi.Response(
#                 description="سفارش یافت نشد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     @action(detail=True, methods=['post'])
#     def cancel(self, request, pk=None):
#         order = self.get_object()
#
#         if order.status not in ['pending', 'paid']:
#             return Response(
#                 {'error': 'فقط سفارش‌های در انتظار پرداخت یا پرداخت شده قابل لغو هستند'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # بازگرداندن آیتم‌ها به موجودی
#         for item in order.items.all():
#             inventory = Inventory.objects.get(product=item.product)
#             inventory.stock += item.quantity
#             inventory.save()
#
#         order.status = 'canceled'
#         order.save()
#
#         return Response({'status': 'سفارش با موفقیت لغو شد'})
#
#     @swagger_auto_schema(
#         operation_summary="پرداخت سفارش",
#         operation_description="انجام پرداخت برای سفارش",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         responses={
#             200: openapi.Response(
#                 description="پرداخت با موفقیت انجام شد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'status': openapi.Schema(type=openapi.TYPE_STRING, example="پرداخت با موفقیت انجام شد")
#                     }
#                 )
#             ),
#             400: openapi.Response(
#                 description="سفارش قابل پرداخت نیست",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'error': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             ),
#             404: openapi.Response(
#                 description="سفارش یافت نشد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     @action(detail=True, methods=['post'])
#     def pay(self, request, pk=None):
#         order = self.get_object()
#
#         if order.status != 'pending':
#             return Response(
#                 {'error': 'فقط سفارش‌های در انتظار پرداخت قابل پرداخت هستند'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         order.status = 'paid'
#         order.paid_at = timezone.now()
#         order.save()
#
#         return Response({'status': 'پرداخت با موفقیت انجام شد'})
#
#     @swagger_auto_schema(
#         operation_summary="ارسال سفارش",
#         operation_description="ثبت ارسال سفارش با کد رهگیری",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=['tracking_code'],
#             properties={
#                 'tracking_code': openapi.Schema(
#                     type=openapi.TYPE_STRING,
#                     description="کد رهگیری ارسال",
#                     example="TRK123456789"
#                 )
#             }
#         ),
#         responses={
#             200: openapi.Response(
#                 description="سفارش با موفقیت ارسال شد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'status': openapi.Schema(type=openapi.TYPE_STRING, example="سفارش با موفقیت ارسال شد")
#                     }
#                 )
#             ),
#             400: openapi.Response(
#                 description="سفارش قابل ارسال نیست یا کد رهگیری ارائه نشده",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'error': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             ),
#             404: openapi.Response(
#                 description="سفارش یافت نشد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     @action(detail=True, methods=['post'])
#     def ship(self, request, pk=None):
#         order = self.get_object()
#
#         if order.status != 'paid':
#             return Response(
#                 {'error': 'فقط سفارش‌های پرداخت شده قابل ارسال هستند'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         tracking_code = request.data.get('tracking_code')
#         if not tracking_code:
#             return Response(
#                 {'error': 'کد رهگیری الزامی است'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         order.status = 'shipped'
#         order.shipped_at = timezone.now()
#         order.tracking_code = tracking_code
#         order.save()
#
#         return Response({'status': 'سفارش با موفقیت ارسال شد'})
#
#     @swagger_auto_schema(
#         operation_summary="تحویل سفارش",
#         operation_description="ثبت تحویل نهایی سفارش",
#         tags=['Orders'],
#         security=[{'Bearer': []}],
#         responses={
#             200: openapi.Response(
#                 description="سفارش با موفقیت تحویل داده شد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'status': openapi.Schema(type=openapi.TYPE_STRING, example="سفارش با موفقیت تحویل داده شد")
#                     }
#                 )
#             ),
#             400: openapi.Response(
#                 description="سفارش قابل تحویل نیست",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'error': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             ),
#             404: openapi.Response(
#                 description="سفارش یافت نشد",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'detail': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     @action(detail=True, methods=['post'])
#     def deliver(self, request, pk=None):
#         order = self.get_object()
#
#         if order.status != 'shipped':
#             return Response(
#                 {'error': 'فقط سفارش‌های ارسال شده قابل تحویل هستند'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         order.status = 'delivered'
#         order.save()
#
#         return Response({'status': 'سفارش با موفقیت تحویل داده شد'})