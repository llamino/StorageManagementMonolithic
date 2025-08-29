# discounts/admin.py

from django.contrib import admin
from .models import ProductDiscount, CategoryUserDiscount, UserDiscount

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'discount_type', 'value', 'start_date', 'end_date', 'is_active']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'product__name', 'description']
    date_hierarchy = 'start_date'
    readonly_fields = ['discount_code']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'product', 'discount_code')
        }),
        ('اطلاعات تخفیف', {
            'fields': ('discount_type', 'value')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )

@admin.register(CategoryUserDiscount)
class CategoryUserDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'category','user', 'discount_type', 'value', 'start_date', 'end_date', 'is_active', 'discount_code']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'category__name', 'description']
    date_hierarchy = 'start_date'
    readonly_fields = ['discount_code']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'category', 'user', 'discount_code')
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
    list_display = ['name', 'user', 'discount_type', 'value', 'min_purchase_amount', 'max_discount_amount', 'is_active', 'discount_code']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'user__email', 'description']
    date_hierarchy = 'start_date'
    readonly_fields = ['discount_code']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'user', 'discount_code')
        }),
        ('اطلاعات تخفیف', {
            'fields': ('discount_type', 'value', 'min_purchase_amount', 'max_discount_amount')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )
