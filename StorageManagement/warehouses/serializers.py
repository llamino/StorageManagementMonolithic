# warehouses/serializers.py

from rest_framework import serializers
from .models import Task, TaskForEmployee, Employee, Warehouse, Inventory, PurchaseOrderFromSupplier, \
    PurchaseOrderDetails
from suppliers.serializers import InventorySupplierSerializer
from products.models import ProductProperty
from products.serializers import ProductPropertySerializer


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description')
        extra_kwargs = {'description': {'required': False}}


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('warehouse', 'tasks', 'manager', 'name', 'last_name', 'phone_number', 'national_code', 'image')
        read_only_fields = ('tasks',)
        extra_kwargs = {'image': {'required': False}}


class TaskForEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskForEmployee
        fields = ('id', 'employee', 'task', 'was_delivered_at', 'is_done')
        read_only_fields = ('id', 'was_delivered_at')


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('name', 'address', 'stablished_date', 'is_full', 'slug')
        read_only_fields = ('stablished_date', 'slug')


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_in_supplier.product.name', read_only=True)

    class Meta:
        model = PurchaseOrderDetails
        fields = [
            'id', 'product_in_supplier', 'product_name',
            'quantity_ordered', 'price_per_unit', 'total_price_item'
        ]
        read_only_fields = ['id', 'product_name', 'total_price_item']


class InventoryListSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    product = ProductPropertySerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'warehouse', 'product', 'stock']
        read_only_fields = ['id', 'warehouse', 'product', 'stock']


class InventoryQuerySerializer(serializers.Serializer):
    warehouse = serializers.CharField(required=False, help_text="فیلتر بر اساس نام انبار")
    product = serializers.IntegerField(required=False, help_text="فیلتر بر اساس آیدی محصول")
    min_stock = serializers.IntegerField(required=False, help_text="حداقل موجودی")
    max_stock = serializers.IntegerField(required=False, help_text="حداکثر موجودی")

class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.CharField(source='supplier.name', read_only=True)
    warehouse = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = PurchaseOrderFromSupplier
        fields = [
            'id', 'supplier', 'warehouse', 'order_date',
            'expected_delivery_date', 'total_price_order', 'is_applied_to_warehouse'
        ]
        read_only_fields = ['id', 'supplier', 'warehouse', 'order_date', 'total_price_order', 'is_applied_to_warehouse']


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.CharField(source='supplier.name', read_only=True)
    warehouse = serializers.CharField(source='warehouse.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True, source='products')

    class Meta:
        model = PurchaseOrderFromSupplier
        fields = [
            'id', 'supplier', 'warehouse', 'order_date', 'expected_delivery_date',
            'total_price_order', 'is_applied_to_warehouse', 'items'
        ]
        read_only_fields = [
            'id', 'supplier', 'warehouse', 'order_date', 'expected_delivery_date',
            'total_price_order', 'is_applied_to_warehouse', 'items'
        ]


class AddProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not ProductProperty.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"محصول با شناسه {value} وجود ندارد.")
        return value


class UpdateProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        if not ProductProperty.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"محصول با شناسه {value} وجود ندارد.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("تعداد نمی‌تواند منفی باشد.")
        return value