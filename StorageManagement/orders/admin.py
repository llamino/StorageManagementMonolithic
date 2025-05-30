# orders/admin.py

from django.contrib import admin
from orders.models import Order, OrderItem
from orders.forms import OrderAdminForm

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'discount', 'discount_reason', 'total_price']
    list_filter = ['order', 'product', 'discount', 'discount_reason']
    search_fields = ['id', 'order__id', 'product__name']
    readonly_fields = ['total_price']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'price', 'discount', 'discount_reason', 'total_price']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product',
            'product__product',
            'product__size',
            'product__color'
        )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ['id', 'user', 'status', 'payment_method', 'total_price', 'final_price', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['id', 'user__email', 'tracking_code', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'paid_at', 'shipped_at', 'final_price']
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'status', 'payment_method', 'shipping_address')
        }),
        ('اطلاعات مالی', {
            'fields': ('total_price', 'discount', 'discount_reason', 'tax', 'shipping_price', 'final_price')
        }),
        ('اطلاعات ارسال', {
            'fields': ('tracking_code', 'notes')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'paid_at', 'shipped_at')
        }),
    )

    def final_price(self, obj):
        return obj.final_price
    final_price.short_description = 'قیمت نهایی'

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='paid', paid_at=timezone.now())
    mark_as_paid.short_description = 'علامت‌گذاری به عنوان پرداخت شده'

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='shipped', shipped_at=timezone.now())
    mark_as_shipped.short_description = 'علامت‌گذاری به عنوان ارسال شده'

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = 'علامت‌گذاری به عنوان تحویل داده شده'

    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')
    mark_as_canceled.short_description = 'علامت‌گذاری به عنوان لغو شده'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'shipping_address'
        ).prefetch_related(
            'items',
            'items__product',
            'items__product__product',
            'items__product__size',
            'items__product__color'
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff
