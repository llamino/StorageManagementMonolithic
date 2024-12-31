from rest_framework.routers import DefaultRouter
from django.urls import path

from . import views

router = DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='tasks')
router.register('employees',views.EmployeeViewSet, basename='employees')
router.register('task_for_employees',views.TaskForEmployeeViewSet, basename='task_for_employees')
router.register('warehouses',views.WarehouseViewSet, basename='warehouses')



urlpatterns = [
    path('warehouse_employees/<str:pk>/',views.WarehouseEmployees.as_view(), name='warehouse_employees'),
    path('employee_tasks/<int:pk>/',views.EmployeeTasks.as_view(), name='employee_tasks'),
    path('purchase_order_from_supplier/',views.PurchaseOrderFromSupplierView.as_view(), name='purchase_order_from_supplier'),
      # نمایش جزئیات یک سفارش
    path('purcahse_order_from_supplier/order/<int:order_id>/', views.PurchaseOrderDetailView.as_view(), name='order-detail'),
      # نمایش لیست تمام سفارش‌ها
    path('purcahse_order_from_supplier/porders/', views.PurchaseOrderListView.as_view(), name='order-list'),
      # لغو سفارش
    path('purcahse_order_from_supplier/order/cancel/<int:order_id>/', views.PurchaseOrderCancelView.as_view(), name='order-cancel'),
] + router.urls