# orders/admin.py

from django.contrib import admin
from orders.models import Order, OrderItem
from orders.forms import OrderAdminForm


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'discount_amount', 'discount_reason', 'total_price']
    list_filter = ['order', 'product']
    search_fields = ['id', 'order__id', 'product__product__name']
    readonly_fields = ['total_price', 'discount_amount', 'discount_reason']
    list_select_related = ['order', 'product', 'product__product']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order',
            'product',
            'product__product',
            'product__size',
            'product__color'
        )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'discount_amount', 'discount_reason']
    fields = ['product', 'quantity', 'price', 'discount_amount', 'discount_reason', 'total_price']
    show_change_link = True

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
    readonly_fields = ['created_at', 'paid_at', 'shipped_at', 'total_price', 'final_price']  # total_price اضافه شد
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled']
    list_select_related = ['user', 'shipping_address']  # اضافه شده برای بهینه‌سازی

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'status', 'payment_method', 'shipping_address')
        }),
        ('اطلاعات مالی', {
            'fields': ('total_price', 'discount', 'discount_reason', 'tax', 'shipping_price', 'final_price'),
            'classes': ('collapse',)  # اضافه شده برای جمع‌شدگی
        }),
        ('اطلاعات ارسال', {
            'fields': ('tracking_code', 'notes'),
            'classes': ('collapse',)  # اضافه شده برای جمع‌شدگی
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'paid_at', 'shipped_at'),
            'classes': ('collapse',)  # اضافه شده برای جمع‌شدگی
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # برای سفارش‌های پرداخت شده، برخی فیلدها را فقط خواندنی می‌کنیم
        if obj and obj.status == 'paid':
            return list(self.readonly_fields) + ['payment_method', 'shipping_address']
        return self.readonly_fields

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(status='paid', paid_at=timezone.now())
        self.message_user(request, f"{updated} سفارش با موفقیت به وضعیت پرداخت شده تغییر یافت")

    mark_as_paid.short_description = 'علامت‌گذاری به عنوان پرداخت شده'

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='paid').update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f"{updated} سفارش با موفقیت به وضعیت ارسال شده تغییر یافت")

    mark_as_shipped.short_description = 'علامت‌گذاری به عنوان ارسال شده'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='shipped').update(status='delivered')
        self.message_user(request, f"{updated} سفارش با موفقیت به وضعیت تحویل داده شده تغییر یافت")

    mark_as_delivered.short_description = 'علامت‌گذاری به عنوان تحویل داده شده'

    def mark_as_canceled(self, request, queryset):
        updated = queryset.exclude(status='delivered').update(status='canceled')
        self.message_user(request, f"{updated} سفارش با موفقیت به وضعیت لغو شده تغییر یافت")

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

    def save_model(self, request, obj, form, change):
        # محاسبه مجدد قیمت‌ها هنگام ذخیره از طریق ادمین
        obj.total_price = obj.calculate_total_price()
        obj.final_price = obj.calculate_final_price()
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # فقط سوپرکاربران می‌توانند سفارش‌ها را حذف کنند
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # فقط کارکنان می‌توانند سفارش‌ها را تغییر دهند
        return request.user.is_staff

    def has_add_permission(self, request):
        # فقط کارکنان می‌توانند سفارش جدید اضافه کنند
        return request.user.is_staff
