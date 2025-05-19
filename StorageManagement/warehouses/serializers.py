from rest_framework import serializers
from .models import Task,TaskForEmployee,Employee,Warehouse,Inventory,PurchaseOrderFromSupplier,PurchaseOrderDetails
from suppliers.serializers import InventorySupplierSerializer
from products.models import ProductProperty
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('title','description')

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('warehouse','tasks','manager','name','last_name','phone_number','national_code','image')
        read_only_fields = ('tasks',)

    # def create(self, validated_data):
    #     manager_object = validated_data.get('manager')
    #     try:
    #         manager = Employee.objects.get(id=manager_object)
    #     except Employee.DoesNotExist:
    #         raise serializers.ValidationError('Employee does not exist')
    #

class TaskForEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskForEmployee
        fields = ('employee','task','was_delivered_at','is_done')
        read_only_fields = ('was_delivered_at',)

    def create(self, validated_data):
        employee_data = validated_data.get('employee')
        task_data = validated_data.get('task')

        if not task_data or employee_data:
            raise serializers.ValidationError({"detail":"task and employee must be entered"})

        if not Employee.objects.get(id=employee_data).exist():
            raise serializers.ValidationError({"detail":"emplyee does not valid"})

        task_object, created = Task.objects.get_or_create(id=task_data)
        instance = TaskForEmployee.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        employee_data = validated_data.get('employee')
        task_data = validated_data.get('task')

        if employee_data is not None:
            if not Employee.objects.get(id=employee_data).exist():
                raise serializers.ValidationError({"detail": "emplyee does not valid"})
            else:
                instance.employee = employee_data
        if task_data is not None:
            task_object, created = Task.objects.get_or_create(id=task_data)
            instance.task = task_data
        return instance

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('name','address','stablished_date','is_full','slug')
        read_only_fields = ('stablished_date','slug')


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای جزئیات هر آیتم سفارش (PurchaseOrderDetails)
    """
    product_name = serializers.CharField(source='product_in_supplier.product.name', read_only=True)
    product = InventorySupplierSerializer(source='product_in_supplier', read_only=True)

    class Meta:
        model = PurchaseOrderDetails
        fields = [
            'id',
            'product_in_supplier',
            'product_name',
            'quantity_ordered',
            'price_per_unit',
            'total_price_item',
            'product',  # شامل اطلاعات تو در تو محصول
        ]
        read_only_fields = ['id', 'product_name', 'total_price_item', 'product']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش لیست سفارش‌ها
    """
    supplier = serializers.CharField(source='supplier.name', read_only=True)
    warehouse = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = PurchaseOrderFromSupplier
        fields = [
            'id',
            'supplier',
            'warehouse',
            'order_date',
            'expected_delivery_date',
            'total_price_order',
            'is_apply_to_inventory',
        ]
        read_only_fields = ['id', 'supplier', 'warehouse', 'order_date', 'total_price_order', 'is_apply_to_inventory']


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش جزئیات کامل یک سفارش (PurchaseOrderFromSupplier) به همراه آیتم‌ها
    """
    supplier = serializers.CharField(source='supplier.name', read_only=True)
    warehouse = serializers.CharField(source='warehouse.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True, source='products')  # related_name='products'

    class Meta:
        model = PurchaseOrderFromSupplier
        fields = [
            'id',
            'supplier',
            'warehouse',
            'order_date',
            'expected_delivery_date',
            'total_price_order',
            'is_apply_to_inventory',
            'items',
        ]
        read_only_fields = [
            'id',
            'supplier',
            'warehouse',
            'order_date',
            'expected_delivery_date',
            'total_price_order',
            'is_apply_to_inventory',
            'items',
        ]


class AddProductSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not ProductProperty.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"محصول با شناسه {value} وجود ندارد.")
        return value
    def validate_quantity(self,value):
        if value < 1:
            raise serializers.ValidationError('تعداد وارد شده معتبر نیست')
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
