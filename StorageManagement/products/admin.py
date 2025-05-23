from django.contrib import admin
from .models import Product, Category, ProductProperty, Size, Color, Comment, ProductRating

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductProperty)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Comment)
admin.site.register(ProductRating)
# Register your models here.
