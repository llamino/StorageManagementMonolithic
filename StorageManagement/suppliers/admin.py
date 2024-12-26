from django.contrib import admin
from .models import Supplier, CategorySupplier, ColorSupplier, SizeSupplier, ProductDetailSupplier,InventorySupplier

from django.contrib.admin import SimpleListFilter

class PriceRangeFilter(SimpleListFilter):
    title = 'Price Range'  # عنوان فیلتر
    parameter_name = 'price'  # پارامتر URL برای فیلتر

    def lookups(self, request, model_admin):
        """تعریف بازه‌های قیمت."""
        return [
            ('0-100', '0 to 100'),
            ('101-500', '101 to 500'),
            ('501-1000', '501 to 1000'),
            ('1001+', 'Above 1000'),
        ]

    def queryset(self, request, queryset):
        """اعمال فیلتر بر اساس بازه انتخابی."""
        if self.value() == '0-100':
            return queryset.filter(price__gte=0, price__lte=100)
        elif self.value() == '101-500':
            return queryset.filter(price__gte=101, price__lte=500)
        elif self.value() == '501-1000':
            return queryset.filter(price__gte=501, price__lte=1000)
        elif self.value() == '1001+':
            return queryset.filter(price__gte=1001)
        return queryset


#---------------------------begin Inline classes-----------------------------------------------

class CategorySupplierProductDetailSupplierInline(admin.TabularInline):
    model = ProductDetailSupplier.categories.through
    extra = 1
    # fields = ('name',)

# class InventoryColorInline(admin.TabularInline):
#     model = ColorSupplier  # Define relationship explicitly
#     extra = 1
#     fields = ('name',)
#
# class InventorySizeInline(admin.TabularInline):
#     model = SizeSuppler  # Define relationship explicitly
#     extra = 1
#     fields = ('name',)



#--------------------------end of Inline classes-----------------------------------------------------


#--------------------------begin admin classes------------------------------------------------
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'is_active',)
    search_fields = ('name', 'phone_number',)
    list_filter = ('is_active',)
    verbose_plural_name = 'Suppliers'

@admin.register(CategorySupplier)
class CategorySupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_plural_name = 'CategorySuppliers'
    inlines = [CategorySupplierProductDetailSupplierInline]

@admin.register(ColorSupplier)
class ColorSupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_plural_name = 'ColorSuppliers'

@admin.register(SizeSupplier)
class SizeSupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_plural_name = 'SizeSuppliers'

@admin.register(ProductDetailSupplier)
class ProductDetailSupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','created_date')
    search_fields = ('name', 'description')
    verbose_plural_name = 'ProductDetailSuppliers'
    inlines = [CategorySupplierProductDetailSupplierInline]


@admin.register(InventorySupplier)
class InventorySupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'colors', 'sizes', 'price')
    search_fields = ('supplier', 'product','price')
    list_filter = ('colors', 'sizes', 'price',PriceRangeFilter)
    ordering = ('supplier', 'product',)
    # inlines = [InventoryColorInline, InventorySizeInline]



#---------------------------end of admin classes-----------------------------------
# Register your models here.
