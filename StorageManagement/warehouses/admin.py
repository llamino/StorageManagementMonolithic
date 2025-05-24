# warehouses/admin.py

from django.contrib import admin
from .models import Inventory,TaskForEmployee, Employee,Warehouse,PurchaseOrderFromSupplier,PurchaseOrderDetails,Task


# -------------------------begin inline classes ---------------------------------------

class TaskForEmployeeInline(admin.TabularInline):
    model = TaskForEmployee
    extra = 1



# ------------------------- end of inline classes -------------------------------------

#--------------------------begin admin classes------------------------------------------------

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # search_fields = ['warehouse', 'product']
    list_display = ['warehouse', 'product', 'stock']
    list_filter = ['stock']
    verbose_name_plural = 'Inventories'



@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['warehouse','name','last_name']
    list_filter = ['warehouse']
    search_fields = ['name','last_name', 'national_code']
    verbose_name_plural = 'Employees'
    inlines = [TaskForEmployeeInline]

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name','slug']
    list_filter = ['is_full']
    search_fields = ['name']
    verbose_name_plural = 'Warehousses'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(PurchaseOrderFromSupplier)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'warehouse', 'order_date', 'is_applied_to_warehouse')
    actions = ['apply_to_inventory']

    def apply_to_inventory(self, request, queryset):
        for order in queryset:
            from .views import ApplyPurchaseToInventory
            view = ApplyPurchaseToInventory()
            response = view.post(request, order.id)
            self.message_user(request, f"Applied order {order.id} to inventory: {response.data.get('detail')}")
    apply_to_inventory.short_description = "Apply selected orders to inventory"

@admin.register(PurchaseOrderDetails)
class PurchaseOrderDetailsAdmin(admin.ModelAdmin):
    list_display = ['product_in_supplier','total_price_item']
    verbose_name_plural = 'Order Details'


@admin.register(TaskForEmployee)
class TaskForEmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee','task','get_warehouse','was_delivered_at', 'is_done']
    def get_warehouse(self,obj):
        #This function displays the warehouse that belongs to an employee who has been assigned a task.
        return obj.employee.warehouse
    get_warehouse.short_description = 'Warehouse'
#---------------------------end of admin classes-----------------------------------
# Register your models here.
