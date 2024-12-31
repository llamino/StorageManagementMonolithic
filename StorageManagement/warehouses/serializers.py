from rest_framework import serializers
from .models import Task,TaskForEmployee,Employee,Warehouse,Inventory,PurchaseOrderFromSupplier,PurchaseOrderDetails


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

    # def create(self, validated_data):
    #     employee_data = validated_data.get('employee')
    #     task_data = validated_data.get('task')
    #
    #     if not task_data or employee_data:
    #         raise serializers.ValidationError({"detail":"task and employee must be entered"})
    #
    #     if not Employee.objects.get(id=employee_data).exist():
    #         raise serializers.ValidationError({"detail":"emplyee does not valid"})
    #
    #     task_object, created = Task.objects.get_or_create(id=task_data)
    #     instance = TaskForEmployee.objects.create(**validated_data)
    #     return instance
    #
    # def update(self, instance, validated_data):
    #     employee_data = validated_data.get('employee')
    #     task_data = validated_data.get('task')
    #
    #     if employee_data is not None:
    #         if not Employee.objects.get(id=employee_data).exist():
    #             raise serializers.ValidationError({"detail": "emplyee does not valid"})
    #         else:
    #             instance.employee = employee_data
    #     if task_data is not None:
    #         task_object, created = Task.objects.get_or_create(id=task_data)
    #         instance.task = task_data
    #     return instance

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('name','address','date_of_establishment','is_full','slug')
        read_only_fields = ('date_of_establishment','slug')

