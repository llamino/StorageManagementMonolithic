# warehouses/views.py

from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import EmployeeSerializer, TaskSerializer, TaskForEmployeeSerializer, WarehouseSerializer, \
    PurchaseOrderListSerializer, AddProductSerializer, UpdateProductSerializer
from .models import Employee,Task,TaskForEmployee,Warehouse, Inventory, PurchaseOrderDetails, PurchaseOrderFromSupplier
from django.db import transaction
from products.models import Product, ProductProperty, Size, Color, Category
from suppliers.models import Supplier, InventorySupplier
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    tags=['Tasks'],
    operation_description="API endpoints for managing warehouse tasks",
)
class TaskViewSet(ModelViewSet):
    """
    ViewSet for managing warehouse tasks.
    Provides CRUD operations for Task objects.
    """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        task_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(task_object)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        task_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(task_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        task_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(task_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        task_object = get_object_or_404(self.queryset, pk=pk)
        task_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    tags=['Employees'],
    operation_description="API endpoints for managing warehouse employees",
)
class EmployeeViewSet(ModelViewSet):
    """
    ViewSet for managing warehouse employees.
    Provides CRUD operations for Employee objects.
    """
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        employee_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(employee_object)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        employee_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(employee_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        employee_object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(employee_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        employee_object = get_object_or_404(self.queryset, pk=pk)
        employee_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    tags=['TaskForEmployees'],
    operation_description="API endpoints for managing tasks assigned to employees",
)
class TaskForEmployeeViewSet(ModelViewSet):
    """
    ViewSet for managing tasks assigned to employees.
    Provides CRUD operations for TaskForEmployee objects.
    """
    serializer_class = TaskForEmployeeSerializer
    queryset = TaskForEmployee.objects.all()
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(object)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def update(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(object, data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def partial_update(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, pk=None):
        object = get_object_or_404(self.queryset, pk=pk)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    tags=['EmployeeTasks'],
    operation_description="API endpoint to list all tasks for a specific employee",
)
class EmployeeTasks(APIView):
    """
    API endpoint to list all tasks for a specific employee.
    """
    # this functions display the tasks that belong to employee who entered by get method request.
    def get(self, request, pk=None):
        employee = get_object_or_404(Employee, id=pk)
        tasks = employee.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    tags=['Warehouses'],
    operation_description="API endpoints for managing warehouses",
)
class WarehouseViewSet(ModelViewSet):
    """
    ViewSet for managing warehouses.
    Provides CRUD operations for Warehouse objects.
    """
    queryset = Warehouse.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer


class WarehouseEmployees(APIView):
    """
    API endpoint to list all employees in a warehouse.
    7777
    """
    @swagger_auto_schema(
        tags=['warehouses'],
        operation_description="API endpoint to list all employees in a warehouse",
        responses={200: EmployeeSerializer(many=True)}
    )
    def get(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse, slug=pk)
        employees = warehouse.employees.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    tags=['PurchaseOrderFromSupplier'],
    operation_description="API endpoint for creating and deleting purchase orders from suppliers",
)
class PurchaseOrderFromSupplierView(APIView):
    """
    API endpoint for creating and deleting purchase orders from suppliers.
    """
    # ایجاد سفارش جدید
    def post(self, request):
        try:
            data = request.data
            supplier_id = data['supplier_id']
            supplier = Supplier.objects.get(name=supplier_id)
            warehouse_id = data['warehouse_id']
            warehouse = Warehouse.objects.get(name=warehouse_id)
            expected_delivery_date = data['expected_delivery_date']
            products = data.get('products', [])
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
                    product = InventorySupplier.objects.get(id=product_id)
                    total_price_item = quantity * product.price
                    if quantity <= 0:
                        raise ValueError(f"Quantity ordered for item {item.id} must be positive.")
                    if product.stock < quantity:
                        raise ValueError('Quantity more than existing stock')
                    PurchaseOrderDetails.objects.create(
                        purchase_order_id=order,
                        product_in_supplier=product,
                        quantity_ordered=quantity,
                        price_per_unit=product.price,
                        total_price_item=total_price_item
                    )
                    order.total_price_order += total_price_item
                    product.stock -= quantity
                    order.save()
                    product.save()
                return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # حذف یک آیتم از سفارش
    # حذف کامل سفارش
    def delete(self, request, order_id):
        try:
            with transaction.atomic():
                order = PurchaseOrderFromSupplier.objects.get(id=order_id)

                # بازگرداندن موجودی محصولات به انبار
                for detail in order.products.all():
                    product = detail.product_in_supplier
                    product.stock += detail.quantity_ordered
                    product.save()

                # حذف جزئیات سفارش
                order.products.all().delete()

                # حذف خود سفارش
                order.delete()

                return Response({"message": "سفارش با موفقیت حذف شد."}, status=status.HTTP_200_OK)

        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "سفارش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # به‌روزرسانی کامل سفارش

    def put(self, request, order_id):
        try:
            data = request.data
            supplier_id = data.get('supplier_id')
            warehouse_id = data.get('warehouse_id')
            expected_delivery_date = data.get('expected_delivery_date')
            products = data.get('products', [])

            with transaction.atomic():
                order = PurchaseOrderFromSupplier.objects.get(id=order_id)

                # به‌روزرسانی تامین‌کننده در صورت ارائه
                if supplier_id:
                    supplier = Supplier.objects.get(name=supplier_id)
                    order.supplier = supplier

                # به‌روزرسانی انبار در صورت ارائه
                if warehouse_id:
                    warehouse = Warehouse.objects.get(name=warehouse_id)
                    order.warehouse = warehouse

                # به‌روزرسانی تاریخ تحویل در صورت ارائه
                if expected_delivery_date:
                    order.expected_delivery_date = expected_delivery_date

                # بازگرداندن موجودی قبلی محصولات
                for detail in order.products.all():
                    product = detail.product_in_supplier
                    product.stock += detail.quantity_ordered
                    product.save()

                # حذف جزئیات سفارش قبلی
                order.products.all().delete()

                # بازنشانی کل قیمت سفارش
                order.total_price_order = 0

                # اضافه کردن محصولات جدید به سفارش
                for item in products:
                    product_id = item['product_in_supplier_id']
                    quantity = item['quantity']
                    product = InventorySupplier.objects.get(id=product_id)
                    total_price_item = quantity * product.price

                    if product.stock < quantity:
                        raise ValueError(f'موجودی محصول با شناسه {product_id} کافی نیست.')

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

                # ذخیره تغییرات سفارش
                order.save()

                return Response({"message": "سفارش با موفقیت به‌روزرسانی شد."}, status=status.HTTP_200_OK)

        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "سفارش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Supplier.DoesNotExist:
            return Response({"error": "تامین‌کننده یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Warehouse.DoesNotExist:
            return Response({"error": "انبار یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except InventorySupplier.DoesNotExist:
            return Response({"error": "محصول یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    tags=['PurchaseOrders'],
    operation_description="API endpoints for managing purchase orders",
)
class PurchaseOrderViewSet(ModelViewSet):
    """
    ViewSet for managing purchase orders.
    Provides CRUD operations for PurchaseOrderFromSupplier objects.
    """
    serializer_class = PurchaseOrderListSerializer  # تعریف serializer_class
    queryset = PurchaseOrderFromSupplier.objects.all()  # تعریف queryset پیش‌فرض

    def get_queryset(self):
        """
        بازنویسی متد get_queryset برای مدیریت درخواست‌ها و جلوگیری از خطا در هنگام تولید اسکیما
        """
        # اگر درخواست برای تولید اسکیما است، یک queryset خالی بازگردانید
        if getattr(self, 'swagger_fake_view', False):
            return PurchaseOrderFromSupplier.objects.none()

        # در غیر این صورت، queryset را به صورت پیش‌فرض بازگردانید
        return super().get_queryset()

    @swagger_auto_schema(
        operation_description="لیست سفارش‌ها با امکان فیلتر بر اساس تامین‌کننده و انبار",
        responses={200: PurchaseOrderListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """
        لیست سفارش‌ها با امکان فیلتر بر اساس تامین‌کننده و انبار
        """
        supplier_name = request.query_params.get('supplier', None)
        warehouse_name = request.query_params.get('warehouse', None)

        orders = self.get_queryset()

        if supplier_name:
            orders = orders.filter(supplier__name__icontains=supplier_name)
        if warehouse_name:
            orders = orders.filter(warehouse__name__icontains=warehouse_name)

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="دریافت جزئیات یک سفارش بر اساس ID",
        responses={
            200: PurchaseOrderListSerializer(),
            404: 'Order not found'
        }
    )
    def retrieve(self, request, pk=None):
        """
        دریافت جزئیات یک سفارش بر اساس ID
        """
        try:
            order = PurchaseOrderFromSupplier.objects.get(id=pk)
            order_details = PurchaseOrderDetails.objects.filter(purchase_order_id=order)

            items = [
                {
                    "id": detail.id,
                    "product_name": detail.product_in_supplier.name,
                    "quantity_ordered": detail.quantity_ordered,
                    "price_per_unit": detail.price_per_unit,
                    "total_price_item": detail.total_price_item
                }
                for detail in order_details
            ]

            response_data = {
                "order_id": order.id,
                "supplier": order.supplier.name,
                "warehouse": order.warehouse.name,
                "expected_delivery_date": order.expected_delivery_date,
                "total_price_order": order.total_price_order,
                "items": items
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="لغو یک سفارش بر اساس ID",
        responses={
            204: 'Order successfully cancelled',
            404: 'Order not found'
        }
    )
    def destroy(self, request, pk=None):
        """
        لغو یک سفارش بر اساس ID
        """
        try:
            order = PurchaseOrderFromSupplier.objects.get(id=pk)

            with transaction.atomic():
                order_details = PurchaseOrderDetails.objects.filter(purchase_order_id=order)
                for detail in order_details:
                    product = detail.product_in_supplier
                    product.stock += detail.quantity_ordered
                    product.save()

                order_details.delete()
                order.delete()

            return Response({"message": "Order successfully cancelled"}, status=status.HTTP_204_NO_CONTENT)

        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    tags=['ApplyPurchaseToInventory'],
    operation_description="Apply a specific purchase order to the warehouse inventory. "
                          "This transfers the ordered items to the warehouse, updates inventory stock, "
                          "and marks the order as applied. If already applied, it will return an error.",
    manual_parameters=[
        openapi.Parameter(
            'order_id',
            openapi.IN_PATH,
            description="ID of the purchase order to apply",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Order successfully applied to inventory', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )),
        400: openapi.Response('Bad Request – Order already applied or supplier stock insufficient'),
        404: openapi.Response('Not Found – Order ID does not exist'),
        500: openapi.Response('Server Error – Unexpected exception')
    }
)
class ApplyPurchaseToInventory(APIView):
    """
    API endpoint to apply a purchase order to inventory.
    """

    def post(self, request, order_id):
        order = get_object_or_404(PurchaseOrderFromSupplier, id=order_id)
        warehouse = order.warehouse
        items = order.products.all()

        if order.is_applied_to_warehouse:
            return Response({'detail': 'This order has already been applied to a warehouse.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                for item in items:
                    quantity = item.quantity_ordered
                    supplier_product = item.product_in_supplier

                    # کاهش موجودی تأمین‌کننده
                    if supplier_product.stock < quantity:
                        return Response({'detail': 'Supplier stock is not sufficient.'}, status=status.HTTP_400_BAD_REQUEST)
                    supplier_product.stock -= quantity
                    supplier_product.save()

                    supplier_product_detail = supplier_product.product
                    supplier_product_color = supplier_product.color.name
                    supplier_product_size = supplier_product.size.name
                    supplier_product_weight = supplier_product.weight
                    supplier_product_price = supplier_product.price
                    supplier_product_name = supplier_product_detail.name
                    supplier_product_description = supplier_product_detail.description
                    supplier_product_categories = supplier_product_detail.categories.all()

                    for category in supplier_product_categories:
                        Category.objects.get_or_create(name=category.name)

                    product_obj, created = Product.objects.get_or_create(
                        name=supplier_product_name,
                        defaults={'description': supplier_product_description}
                    )

                    if created:
                        product_obj.categories.set(
                            [Category.objects.get(name=cat.name) for cat in supplier_product_categories]
                        )

                    color_obj, _ = Color.objects.get_or_create(name=supplier_product_color)
                    size_obj, _ = Size.objects.get_or_create(name=supplier_product_size)

                    product_property, _ = ProductProperty.objects.get_or_create(
                        product=product_obj,
                        color=color_obj,
                        size=size_obj,
                        defaults={
                            'weight': supplier_product_weight,
                            'buy_price': supplier_product_price
                        }
                    )

                    # در صورتی که از قبل وجود داشته باشد، ویژگی‌ها را به‌روز کنیم
                    if not _:
                        product_property.weight = supplier_product_weight
                        product_property.buy_price = supplier_product_price
                        product_property.save()

                    inventory_obj, created = Inventory.objects.get_or_create(
                        warehouse=warehouse,
                        product=product_property
                    )

                    if created:
                        inventory_obj.stock = quantity
                    else:
                        inventory_obj.stock += quantity

                    inventory_obj.save()

                # به‌روزرسانی وضعیت سفارش
                order.is_applied_to_warehouse = True
                order.save()

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Order successfully applied to inventory'}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    tags=['AddProductToInventory'],
    operation_description="API endpoint to add a product to warehouse inventory",
)
class AddProductToInventory(APIView):
    """
    API endpoint to add a product to warehouse inventory.
    """
    '''
    این کلاس برای افزودن یک یا چند محصول به انبار مشخصه ایجاد شده است.
    ورودی هایی که نیاز است در این کلاس در اختیار داشته باشیم، عبارت است از:
    - شناسه انبار مورد نظر (warehouse_name)
    - لیستی از محصولات شامل شناسه محصول و تعداد مورد نظر برای افزایش
    '''

    def post(self, request, warehouse_name):
        """
        دریافت یک لیست از محصولات و تعداد آنها و افزودن به انبار مشخص.
        """
        warehouse = get_object_or_404(Warehouse, name=warehouse_name)

        serializer = AddProductSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        products_data = serializer.validated_data

        # عملیات افزودن محصولات به انبار با استفاده از تراکنش برای اطمینان از یکپارچگی داده‌ها
        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item['product_id']
                    quantity = item['quantity']

                    # دریافت محصول
                    product = get_object_or_404(ProductProperty, id=product_id)

                    # به‌روزرسانی یا ایجاد موجودی
                    inventory, created = Inventory.objects.get_or_create(
                        warehouse=warehouse,
                        product=product,
                        defaults={'stock': quantity}
                    )
                    if not created:
                        inventory.stock += quantity
                        inventory.save()

            return Response({"detail": "محصولات با موفقیت به انبار اضافه شدند."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "خطایی رخ داد.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    tags=['UpdateProductInventory'],
    operation_description="API endpoint to update a product in warehouse inventory",
)
class UpdateProductInventory(APIView):
    """
    API endpoint to update a product in warehouse inventory.
    """
    '''
    این کلاس برای بروز رسانی موجودی یک محصول در انبار مشخصه ایجاد شده است.
    ورودی هایی که نیاز است عبارتند از:
    - شناسه انبار مورد نظر (warehouse_name)
    - شناسه محصول
    - تعداد جدید برای موجودی (stock)
    '''

    def put(self, request, warehouse_name):
        """
        بروز رسانی موجودی محصولات در انبار مشخص.
        """
        # اعتبارسنجی انبار
        warehouse = get_object_or_404(Warehouse, name=warehouse_name)

        # اعتبارسنجی داده‌های ورودی
        serializer = UpdateProductSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        products_data = serializer.validated_data

        # عملیات بروز رسانی موجودی
        try:
            with transaction.atomic():
                for item in products_data:
                    product_id = item['product_id']
                    new_quantity = item['quantity']

                    # دریافت محصول
                    product = get_object_or_404(ProductProperty, id=product_id)

                    # دریافت موجودی
                    inventory = Inventory.objects.filter(warehouse=warehouse, product=product).first()
                    if inventory:
                        inventory.stock = new_quantity
                        inventory.save()
                    else:
                        return Response(
                            {"detail": f"محصول با شناسه {product_id} در انبار {warehouse_name} وجود ندارد."},
                            status=status.HTTP_404_NOT_FOUND
                        )

            return Response({"detail": "موجودی محصولات با موفقیت بروز رسانی شد."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "خطایی رخ داد.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    tags=['DeleteProductFromInventory'],
    operation_description="API endpoint to delete a product from warehouse inventory",
)
class DeleteProductFromInventory(APIView):
    """
    API endpoint to delete a product from warehouse inventory.
    """
    '''
    این کلاس برای حذف یک محصول از انبار مشخصه ایجاد شده است.
    ورودی هایی که نیاز است عبارتند از:
    - شناسه انبار مورد نظر (warehouse_name)
    - شناسه محصول
    '''

    def delete(self, request, warehouse_name, product_id):
        """
        حذف یک محصول از انبار مشخص.
        """
        warehouse = get_object_or_404(Warehouse, name=warehouse_name)

        product = get_object_or_404(ProductProperty, id=product_id)

        try:
            inventory = Inventory.objects.filter(warehouse=warehouse, product=product).first()
            if inventory:
                inventory.delete()
                return Response({"detail": "محصول با موفقیت از انبار حذف شد."}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": f"محصول با شناسه {product_id} در انبار {warehouse_name} وجود ندارد."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({"detail": "خطایی رخ داد.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransmitWarehouseProduct(APIView):
    """
    API endpoint to transmit a product between warehouses.
    """

    @swagger_auto_schema(
        tags=['warehouses'],
        operation_description="API endpoint to transmit a product between warehouses",
        request_body=AddProductSerializer(many=True)
    )
    def post(self, request, origin_warehouse_name, destination_warehouse_name):
        origin_warehouse = get_object_or_404(Warehouse, name=origin_warehouse_name)
        destination_warehouse = get_object_or_404(Warehouse, name=destination_warehouse_name)
        raw_data = request.data
        if isinstance(raw_data, dict) and "data" in raw_data:
            data = raw_data["data"]
        else:
            data = raw_data

        serializer = AddProductSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        products = serializer.validated_data
        try:
            with transaction.atomic():
                for item in products:
                    product = ProductProperty.objects.get(id=item['product_id'])
                    try:
                        origin_inventory = Inventory.objects.get(warehouse=origin_warehouse, product=product)
                    except:
                        raise ValueError('انبار مبدا،‌ محصول مورد نظر را ندارد')
                    if origin_inventory.stock < item['quantity']:
                        raise ValueError(f'تعدادی که وارد کردید، از موجودی محصول {item} بیشتر است ')
                    destination_inventory, created = Inventory.objects.get_or_create(warehouse=destination_warehouse, product=product)
                    if created:
                        destination_inventory.stock = item['quantity']
                    else:
                        destination_inventory.stock += item['quantity']
                    origin_inventory.stock -= item['quantity']
                    Inventory.objects.bulk_update(
                        [destination_inventory, origin_inventory], ["stock"]
                    )
                return Response({"detail": "محصولات با موفقیت به انبار اضافه شدند."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "خطایی رخ داد.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





