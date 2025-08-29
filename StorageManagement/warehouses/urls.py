# warehouses/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='tasks')
router.register('employees', views.EmployeeViewSet, basename='employees')
router.register('task_for_employees', views.TaskForEmployeeViewSet, basename='task_for_employees')
router.register('warehouses', views.WarehouseViewSet, basename='warehouses')

urlpatterns = [
    path('warehouse_employees/<str:pk>/', views.WarehouseEmployees.as_view(), name='warehouse_employees'),
    path('employee_tasks/<int:pk>/', views.EmployeeTasks.as_view(), name='employee_tasks'),
    path('purchase-orders/', views.PurchaseOrderFromSupplierView.as_view(), name='purchaseorder-create'),
    path('purchase-orders/<int:order_id>/', views.PurchaseOrderFromSupplierView.as_view(), name='purchaseorder-detail'),
    path('apply_purchase_to_inventory/<int:order_id>/', views.ApplyPurchaseToInventory.as_view(), name='apply_purchase'),
    path('inventory/add/<str:warehouse_name>/', views.AddProductToInventory.as_view(), name='add_product_to_inventory'),
    path('inventory/update/<str:warehouse_name>/', views.UpdateProductInventory.as_view(), name='update_product_inventory'),
    path('inventory/delete/<str:warehouse_name>/<int:product_id>/', views.DeleteProductFromInventory.as_view(), name='delete_product_from_inventory'),
    path('inventory/transmit/<str:origin_warehouse_name>/<str:destination_warehouse_name>/', views.TransmitWarehouseProduct.as_view(), name='transmit_warehouse_product'),
    path('inventories/', views.InventoryListView.as_view(), name='inventory-list'),
] + router.urls