from django.contrib import admin
from .models import Product, Category, ProductProperty, Size, Color

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductProperty)
admin.site.register(Size)
admin.site.register(Color)
# Register your models here.
