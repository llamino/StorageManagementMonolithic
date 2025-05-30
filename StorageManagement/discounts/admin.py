# discounts/admin.py

from django.contrib import admin
from .models import ProductDiscount, CategoryDiscount, UserDiscount

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'discount_type', 'value', 'start_date', 'end_date', 'is_active']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'product__name', 'description']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'product')
        }),
        ('اطلاعات تخفیف', {
            'fields': ('discount_type', 'value')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )

@admin.register(CategoryDiscount)
class CategoryDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'discount_type', 'value', 'start_date', 'end_date', 'is_active']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'category__name', 'description']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'category')
        }),
        ('اطلاعات تخفیف', {
            'fields': ('discount_type', 'value')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )

@admin.register(UserDiscount)
class UserDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'discount_type', 'value', 'min_purchase_amount', 'max_discount_amount', 'is_active']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'user__email', 'description']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'user')
        }),
        ('اطلاعات تخفیف', {
            'fields': ('discount_type', 'value', 'min_purchase_amount', 'max_discount_amount')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )
