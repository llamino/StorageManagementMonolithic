# warehouses/views.py

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    TaskSerializer, EmployeeSerializer, TaskForEmployeeSerializer,
    WarehouseSerializer, PurchaseOrderListSerializer, AddProductSerializer,
    UpdateProductSerializer, PurchaseOrderDetailSerializer, InventoryListSerializer, InventoryQuerySerializer
)
from .models import (
    Task, Employee, TaskForEmployee, Warehouse, Inventory,
    PurchaseOrderFromSupplier, PurchaseOrderDetails
)
from products.models import Product, ProductProperty, Category, Color, Size
from suppliers.models import Supplier, InventorySupplier


class TaskViewSet(ModelViewSet):
    """
    ViewSet for managing warehouse tasks.
    Provides CRUD operations for Task objects.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class EmployeeViewSet(ModelViewSet):
    """
    ViewSet for managing warehouse employees.
    Provides CRUD operations for Employee objects.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


class TaskForEmployeeViewSet(ModelViewSet):
    """
    ViewSet for managing tasks assigned to employees.
    Provides CRUD operations for TaskForEmployee objects.
    """
    queryset = TaskForEmployee.objects.all()
    serializer_class = TaskForEmployeeSerializer
    permission_classes = [IsAuthenticated]


class EmployeeTasks(APIView):
    """
    API endpoint to list all tasks for a specific employee.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all tasks for a specific employee",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, pk=None):
        employee = get_object_or_404(Employee, id=pk)
        tasks = employee.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WarehouseViewSet(ModelViewSet):
    """
    ViewSet for managing warehouses.
    Provides CRUD operations for Warehouse objects.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]


class WarehouseEmployees(APIView):
    """
    API endpoint to list all employees in a warehouse.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all employees in a specific warehouse",
        responses={200: EmployeeSerializer(many=True)}
    )
    def get(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse, slug=pk)
        employees = warehouse.employees.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PurchaseOrderFromSupplierView(APIView):
    """
    API endpoint for creating, updating and deleting purchase orders from suppliers.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new purchase order",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'supplier_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'warehouse_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'expected_delivery_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'products': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'product_in_supplier_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            }
        ),
        responses={
            201: PurchaseOrderDetailSerializer,
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def post(self, request):
        try:
            data = request.data
            supplier_id = data['supplier_id']
            warehouse_id = data['warehouse_id']
            expected_delivery_date = data['expected_delivery_date']
            products = data.get('products', [])

            supplier = get_object_or_404(Supplier, id=supplier_id)
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)

            with transaction.atomic():
                total_price_order = 0
                order = PurchaseOrderFromSupplier.objects.create(
                    supplier=supplier,
                    warehouse=warehouse,
                    expected_delivery_date=expected_delivery_date,
                    total_price_order=total_price_order
                )

                for item in products:
                    product_id = item['product_in_supplier_id']
                    quantity = item['quantity']
                    product = get_object_or_404(InventorySupplier, id=product_id)

                    if quantity <= 0:
                        raise ValueError(f"Quantity ordered for item {product_id} must be positive.")

                    if product.stock < quantity:
                        raise ValueError(f'Quantity more than existing stock for product {product.product.name}')

                    total_price_item = quantity * product.price

                    PurchaseOrderDetails.objects.create(
                        purchase_order_id=order,
                        product_in_supplier=product,
                        quantity_ordered=quantity,
                        price_per_unit=product.price,
                        total_price_item=total_price_item
                    )

                    order.total_price_order += total_price_item
                    product.stock -= quantity
                    product.save()

                order.save()

                serializer = PurchaseOrderDetailSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a purchase order",
        responses={
            200: 'Order deleted successfully',
            404: 'Order not found'
        }
    )
    def delete(self, request, order_id):
        try:
            with transaction.atomic():
                order = get_object_or_404(PurchaseOrderFromSupplier, id=order_id)

                # Return stock to supplier
                for detail in order.products.all():
                    product = detail.product_in_supplier
                    if product:
                        product.stock += detail.quantity_ordered
                        product.save()

                # Delete order details and order
                order.products.all().delete()
                order.delete()

                return Response({"message": "سفارش با موفقیت حذف شد."}, status=status.HTTP_200_OK)

        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "سفارش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApplyPurchaseToInventory(APIView):
    """
    API endpoint to apply a purchase order to inventory.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Apply a purchase order to inventory",
        responses={
            200: 'Order successfully applied to inventory',
            400: 'Order already applied or insufficient stock',
            404: 'Order not found'
        }
    )
    def post(self, request, order_id):
        order = get_object_or_404(PurchaseOrderFromSupplier, id=order_id)

        if order.is_applied_to_warehouse:
            return Response(
                {'detail': 'This order has already been applied to a warehouse.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                for item in order.products.all():
                    quantity = item.quantity_ordered
                    supplier_product = item.product_in_supplier
                    warehouse = order.warehouse

                    # Check supplier stock
                    if supplier_product.stock < quantity:
                        return Response(
                            {'detail': 'Supplier stock is not sufficient.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Get or create product properties
                    product_property, created = ProductProperty.objects.get_or_create(
                        product=supplier_product.product,
                        color=supplier_product.color,
                        size=supplier_product.size,
                        defaults={
                            'weight': supplier_product.weight,
                            'buy_price': supplier_product.price
                        }
                    )

                    # Update or create inventory
                    inventory, created = Inventory.objects.get_or_create(
                        warehouse=warehouse,
                        product=product_property,
                        defaults={'stock': quantity}
                    )

                    if not created:
                        inventory.stock += quantity
                        inventory.save()

                    # Update supplier stock
                    supplier_product.stock -= quantity
                    supplier_product.save()

                # Mark order as applied
                order.is_applied_to_warehouse = True
                order.save()

                return Response(
                    {'detail': 'Order successfully applied to inventory'},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddProductToInventory(APIView):
    """
    API endpoint to add a product to warehouse inventory.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add products to warehouse inventory",
        request_body=AddProductSerializer(many=True),
        responses={
            200: 'Products added successfully',
            400: 'Invalid data',
            404: 'Warehouse or product not found'
        }
    )
    def post(self, request, warehouse_name):
        warehouse = get_object_or_404(Warehouse, name=warehouse_name)

        serializer = AddProductSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        products_data = serializer.validated_data

        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item['product_id']
                    quantity = item['quantity']

                    product = get_object_or_404(ProductProperty, id=product_id)

                    inventory, created = Inventory.objects.get_or_create(
                        warehouse=warehouse,
                        product=product,
                        defaults={'stock': quantity}
                    )

                    if not created:
                        inventory.stock += quantity
                        inventory.save()

            return Response(
                {"detail": "محصولات با موفقیت به انبار اضافه شدند."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "خطایی رخ داد.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InventoryListView(APIView):
    """
    API endpoint برای دریافت لیست موجودی‌های انبارها
    """
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        دریافت لیست کامل موجودی‌های تمامی انبارها با امکان فیلتر

        امکان فیلتر بر اساس:
        - نام انبار (warehouse)
        - آیدی محصول (product)
        - محدوده موجودی (min_stock و max_stock)
        """,
        manual_parameters=[
            openapi.Parameter(
                'warehouse',
                openapi.IN_QUERY,
                description="نام انبار برای فیلتر",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'product',
                openapi.IN_QUERY,
                description="آیدی محصول برای فیلتر",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'min_stock',
                openapi.IN_QUERY,
                description="حداقل موجودی",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'max_stock',
                openapi.IN_QUERY,
                description="حداکثر موجودی",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: InventoryListSerializer(many=True),
            400: 'داده‌های ورودی نامعتبر',
            401: 'عدم دسترسی',
            500: 'خطای سرور'
        }
    )
    def get(self, request):
        # اعتبارسنجی پارامترهای کوئری
        query_serializer = InventoryQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(
                query_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = query_serializer.validated_data

        try:
            # شروع کوئری‌بیس
            inventories = Inventory.objects.select_related(
                'warehouse', 'product'
            ).all()

            # اعمال فیلترها
            if 'warehouse' in validated_data:
                inventories = inventories.filter(
                    warehouse__name__icontains=validated_data['warehouse']
                )

            if 'product' in validated_data:
                inventories = inventories.filter(
                    product__id=validated_data['product']
                )

            if 'min_stock' in validated_data:
                inventories = inventories.filter(
                    stock__gte=validated_data['min_stock']
                )

            if 'max_stock' in validated_data:
                inventories = inventories.filter(
                    stock__lte=validated_data['max_stock']
                )

            # سریالایز کردن داده‌ها
            serializer = InventoryListSerializer(inventories, many=True)

            return Response({
                'count': inventories.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    'detail': 'خطایی در دریافت لیست موجودی‌ها رخ داد',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateProductInventory(APIView):
    """
    API endpoint to update a product in warehouse inventory.
    """
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update product quantities in warehouse inventory",
        request_body=UpdateProductSerializer(many=True),
        responses={
            200: 'Inventory updated successfully',
            400: 'Invalid data',
            404: 'Warehouse or product not found'
        }
    )
    def put(self, request, warehouse_name):
        warehouse = get_object_or_404(Warehouse, name=warehouse_name)

        serializer = UpdateProductSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        products_data = serializer.validated_data

        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item['product_id']
                    new_quantity = item['quantity']

                    product = get_object_or_404(ProductProperty, id=product_id)

                    inventory = get_object_or_404(
                        Inventory,
                        warehouse=warehouse,
                        product=product
                    )

                    inventory.stock = new_quantity
                    inventory.save()

            return Response(
                {"detail": "موجودی محصولات با موفقیت بروز رسانی شد."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "خطایی رخ داد.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteProductFromInventory(APIView):
    """
    API endpoint to delete a product from warehouse inventory.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a product from warehouse inventory",
        responses={
            200: 'Product deleted successfully',
            404: 'Warehouse or product not found'
        }
    )
    def delete(self, request, warehouse_name, product_id):
        warehouse = get_object_or_404(Warehouse, name=warehouse_name)
        product = get_object_or_404(ProductProperty, id=product_id)

        try:
            inventory = get_object_or_404(
                Inventory,
                warehouse=warehouse,
                product=product
            )

            inventory.delete()
            return Response(
                {"detail": "محصول با موفقیت از انبار حذف شد."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "خطایی رخ داد.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransmitWarehouseProduct(APIView):
    """
    API endpoint to transfer products between warehouses.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Transfer products between warehouses",
        request_body=AddProductSerializer(many=True),
        responses={
            200: 'Products transferred successfully',
            400: 'Invalid data or insufficient stock',
            404: 'Warehouse or product not found'
        }
    )
    def post(self, request, origin_warehouse_name, destination_warehouse_name):
        origin_warehouse = get_object_or_404(Warehouse, name=origin_warehouse_name)
        destination_warehouse = get_object_or_404(Warehouse, name=destination_warehouse_name)

        serializer = AddProductSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        products_data = serializer.validated_data

        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item['product_id']
                    quantity = item['quantity']

                    product = get_object_or_404(ProductProperty, id=product_id)

                    # استفاده از try-except برای مدیریت خطای موجودی
                    try:
                        origin_inventory = Inventory.objects.get(
                            warehouse=origin_warehouse,
                            product=product
                        )
                    except Inventory.DoesNotExist:
                        raise ValueError(f"موجودی محصول {product_id} در انبار مبدا یافت نشد")

                    if origin_inventory.stock < quantity:
                        raise ValueError(f"تعداد درخواستی برای محصول {product_id} بیش از موجودی است")

                    destination_inventory, created = Inventory.objects.get_or_create(
                        warehouse=destination_warehouse,
                        product=product,
                        defaults={'stock': quantity}
                    )

                    if not created:
                        destination_inventory.stock += quantity
                        destination_inventory.save()

                    origin_inventory.stock -= quantity
                    origin_inventory.save()

                return Response(
                    {"detail": "محصولات با موفقیت انتقال یافتند."},
                    status=status.HTTP_200_OK
                )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": "خطایی رخ داد.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
