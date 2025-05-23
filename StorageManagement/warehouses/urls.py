# warehouses/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path

from . import views

router = DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='tasks')
router.register('employees',views.EmployeeViewSet, basename='employees')
router.register('task_for_employees',views.TaskForEmployeeViewSet, basename='task_for_employees')
router.register('warehouses',views.WarehouseViewSet, basename='warehouses')
# نمایش جزئیات یک سفارش - نمایش لیست تمام سفارش ها - لغو سفارش
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchaseorder')



urlpatterns = [
    # نمایش کارمندهای یک انبار مشخص
    path('warehouse_employees/<str:pk>/',views.WarehouseEmployees.as_view(), name='warehouse_employees'),
    # نمایش وظیفه های نگاشته شده برای یک کاربر مشخص
    path('employee_tasks/<int:pk>/',views.EmployeeTasks.as_view(), name='employee_tasks'),
    # مسیر برای ایجاد سفارش جدید (POST) - به روز رسانی یک سفارش همراه با اقلام آن - حذف یک سفارش به همراه اقلام ان سفارش
    path('purchase-orders/<int:order_id>/', views.PurchaseOrderFromSupplierView.as_view(), name='purchaseorder-create'),
    # مسیر برای حذف و به‌روزرسانی یک آیتم در سفارش
    path('purchase-orders/items/<int:order_id>/<int:detail_id>/', views.PurchaseOrderFromSupplierView.as_view(),name='purchaseorder-item'),
    # اعمال نهایی خرید و انجام سفارش و سپس انتقال محصولات سفارش مورد نظر به انبار مورد نظر و همچنین ثبت محصولات جدیدی که قبلا مشخصات آنها در جدول product ثبت نشده بود
    path('apply_purchase_to_inventory/<int:order_id>', views.ApplyPurchaseToInventory.as_view(),name='apply_purchase'),
    # افزودن محصولات به انبار
    path('inventory/add/<str:warehouse_name>/', views.AddProductToInventory.as_view(),name='add_product_to_inventory'),
    # بروز رسانی موجودی محصول در انبار
    path('inventory/update/<str:warehouse_name>/', views.UpdateProductInventory.as_view(),name='update_product_inventory'),
    # حذف موجودی محصول مورد نظر در انبار
    path('inventory/delete/<str:warehouse_name>/<int:product_id>/', views.DeleteProductFromInventory.as_view(),name='delete_product_from_inventory'),
    # انتقال محصولاتی از یک انبار به انبار دیگر
    path('inventory/transmit/<str:origin_warehouse_name>/<str:destination_warehouse_name>/', views.TransmitWarehouseProduct.as_view(),name='transmit_warehouse_product')
] + router.urls