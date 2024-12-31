from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import EmployeeSerializer, TaskSerializer, TaskForEmployeeSerializer, WarehouseSerializer
from .models import Employee,Task,TaskForEmployee,Warehouse, Inventory, PurchaseOrderDetails, PurchaseOrderFromSupplier
from django.db import transaction
from products.models import Product, ProductProperty, Size, Color, Category
from suppliers.models import Supplier, InventorySupplier


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

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

class EmployeeViewSet(ModelViewSet):
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

class TaskForEmployeeViewSet(ModelViewSet):
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

class EmployeeTasks(APIView):
    # this functions display the tasks that belong to employee who entered by get method request.
    def get(self, request, pk=None):
        employee = get_object_or_404(Employee, id=pk)
        tasks = employee.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WarehouseViewSet(ModelViewSet):
    queryset = Warehouse.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer

class WarehouseEmployees(APIView):
    def get(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse, slug=pk)
        employees = warehouse.employees.all()
        seializer = EmployeeSerializer(employees,many=True)
        return Response(seializer.data, status=status.HTTP_200_OK)


class PurchaseOrderFromSupplierView(APIView):

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
    def delete(self, request, order_id, detail_id):
        try:
            with transaction.atomic():
                order = PurchaseOrderFromSupplier.objects.get(id=order_id)
                detail = PurchaseOrderDetails.objects.get(id=detail_id, purchase_order_id=order)
                # بازگرداندن موجودی محصول به انبار
                product = detail.product_in_supplier
                product.stock += detail.quantity_ordered
                product.save()
                # کاهش قیمت آیتم از کل سفارش
                order.total_price_order -= detail.total_price_item
                order.save()
                # حذف آیتم
                detail.delete()
                return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)
        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except PurchaseOrderDetails.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # به‌روزرسانی یک آیتم در سفارش
    def put(self, request, order_id, detail_id):
        try:
            data = request.data
            new_quantity = data['quantity']
            with transaction.atomic():
                order = PurchaseOrderFromSupplier.objects.get(id=order_id)
                detail = PurchaseOrderDetails.objects.get(id=detail_id, purchase_order_id=order)
                product = detail.product_in_supplier
                # محاسبه تغییرات موجودی
                quantity_difference = new_quantity - detail.quantity_ordered
                if product.stock < quantity_difference:
                    raise ValueError('Not enough stock to update quantity')
                # به‌روزرسانی موجودی محصول
                product.stock -= quantity_difference
                product.save()
                # به‌روزرسانی جزئیات سفارش
                detail.quantity_ordered = new_quantity
                detail.total_price_item = new_quantity * product.price
                detail.save()
                # به‌روزرسانی کل قیمت سفارش
                order.total_price_order += quantity_difference * product.price
                order.save()
                return Response({"message": "Item updated successfully"}, status=status.HTTP_200_OK)
        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except PurchaseOrderDetails.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)











        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PurchaseOrderDetailView(APIView):
    def get(self, request, order_id):
        try:
            # دریافت سفارش از طریق ID
            order = PurchaseOrderFromSupplier.objects.get(id=order_id)
            # دریافت آیتم‌های مربوط به سفارش
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

            # ساخت پاسخ JSON
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


class PurchaseOrderListView(APIView):
    def get(self, request):
        # فیلترهای اختیاری از پارامترهای query برای جستجو
        supplier_name = request.query_params.get('supplier', None)
        warehouse_name = request.query_params.get('warehouse', None)

        # فیلتر کردن سفارش‌ها
        orders = PurchaseOrderFromSupplier.objects.all()

        if supplier_name:
            orders = orders.filter(supplier__name__icontains=supplier_name)
        if warehouse_name:
            orders = orders.filter(warehouse__name__icontains=warehouse_name)

        # تبدیل داده‌ها به فرمت مناسب JSON
        response_data = [
            {
                "order_id": order.id,
                "supplier": order.supplier.name,
                "warehouse": order.warehouse.name,
                "expected_delivery_date": order.expected_delivery_date,
                "total_price_order": order.total_price_order
            }
            for order in orders
        ]

        return Response(response_data, status=status.HTTP_200_OK)


class PurchaseOrderCancelView(APIView):
    def delete(self, request, order_id):
        try:
            # دریافت سفارش از طریق ID
            order = PurchaseOrderFromSupplier.objects.get(id=order_id)

            with transaction.atomic():
                # برگرداندن موجودی هر محصول به انبار
                order_details = PurchaseOrderDetails.objects.filter(purchase_order_id=order)
                for detail in order_details:
                    product = detail.product_in_supplier
                    product.stock += detail.quantity_ordered
                    product.save()

                # حذف آیتم‌های سفارش
                order_details.delete()

                # حذف خود سفارش
                order.delete()

            return Response({"message": "Order successfully cancelled"}, status=status.HTTP_204_NO_CONTENT)

        except PurchaseOrderFromSupplier.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)