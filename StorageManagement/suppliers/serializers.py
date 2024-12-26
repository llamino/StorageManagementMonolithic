from rest_framework import serializers
from .models import CategorySupplier,SizeSupplier,ColorSupplier,ProductDetailSupplier,InventorySupplier,Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('name','phone_number','address','is_active')

class CategorySupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySupplier
        fields = ('name',)

class SizeSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeSupplier
        fields = ('name')

class ColorSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorSupplier
        fields = ('name')

class ProductDetailSupplierSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategorySupplier.objects.all()
    )

    class Meta:
        model = ProductDetailSupplier
        fields = ['name', 'description', 'categories', 'created_date']

    def create(self, validated_data):
        # استخراج داده‌های دسته‌بندی
        categories_data = validated_data.pop('categories', [])

        # ساخت محصول جدید و اضافه کردن دسته‌بندی‌ها
        product = ProductDetailSupplier.objects.create(**validated_data)
        product.categories.set(categories_data)  # اضافه کردن دسته‌بندی‌ها
        return product

    def update(self, instance, validated_data):
        # استخراج داده‌های دسته‌بندی
        categories_data = validated_data.pop('categories', [])

        # به‌روزرسانی فیلدهای محصول
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # اگر `categories` در ورودی وجود داشت، دسته‌بندی‌ها را به‌روزرسانی کنید
        if categories_data is not None:
            instance.categories.set(categories_data)  # جایگزینی دسته‌بندی‌ها فقط در صورت وجود
        return instance

