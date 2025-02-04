from rest_framework import serializers
from .models import Size,Color,Category,ProductRating,ProductProperty,Product
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('name',)

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('name',)

class CategorySerializer(serializers.Serializer):
    class Meta:
        model = Category
        fields = ('name',)

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)  # سریالایزر برای دسته‌بندی‌ها

    class Meta:
        model = Product
        fields = ['name', 'description', 'categories', 'created_date']

    def create(self, validated_data):
        # استخراج دسته‌بندی‌ها از داده‌های معتبر
        categories_data = validated_data.pop('categories', [])

        # ایجاد محصول جدید
        product = Product.objects.create(**validated_data)

        for category_data in categories_data:
            category_name = category_data.get('name')  # استخراج نام دسته‌بندی
            category, created = Category.objects.get_or_create(name=category_name)

            # اضافه کردن دسته‌بندی به محصول
            product.categories.add(category)

        return product

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', [])

        # به‌روزرسانی فیلدهای محصول
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories_data:
            # استخراج نام دسته‌بندی‌ها
            unique_categories = set(
                category_data.get('name') for category_data in categories_data if category_data.get('name')
            )

            # گرفتن یا ایجاد دسته‌بندی‌ها
            existing_categories = Category.objects.filter(name__in=unique_categories)
            existing_category_names = set(cat.name for cat in existing_categories)

            new_categories = [
                Category(name=name) for name in unique_categories if name not in existing_category_names
            ]
            Category.objects.bulk_create(new_categories)

            # تنظیم دسته‌بندی‌ها برای محصول
            all_categories = Category.objects.filter(name__in=unique_categories)
            instance.categories.set(all_categories)

        return instance


class InventorySupplierSerializer(serializers.ModelSerializer):
    sizes = serializers.CharField(required=False, allow_blank=True)
    colors = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ProductProperty
        fields = ('id', 'supplier', 'product', 'stock', 'colors', 'sizes', 'weight', 'price')

    def create(self, validated_data):
        # استخراج داده‌ها
        supplier_data = validated_data.pop('supplier', None)
        sizes_data = validated_data.pop('sizes', None)
        colors_data = validated_data.pop('colors', None)

        # بررسی اینکه supplier حتما وارد شده باشد
        if not supplier_data:
            raise serializers.ValidationError({"supplier": "اطلاعات تامین‌کننده الزامی است."})

        # گرفتن یا ایجاد اشیاء
        supplier_object, created = Supplier.objects.get_or_create(name=supplier_data)

        size_object = None
        if sizes_data:
            size_object, created = SizeSupplier.objects.get_or_create(name=sizes_data)

        colors_object = None
        if colors_data:
            colors_object, created = ColorSupplier.objects.get_or_create(name=colors_data)

        # ایجاد نمونه جدید
        instance = InventorySupplier.objects.create(
            supplier=supplier_object,
            sizes=size_object,
            colors=colors_object,
            **validated_data
        )
        return instance

    def update(self, instance, validated_data):
        # استخراج داده‌ها
        supplier_data = validated_data.pop('supplier', None)
        sizes_data = validated_data.pop('sizes', None)
        colors_data = validated_data.pop('colors', None)

        # به‌روزرسانی تامین‌کننده
        if supplier_data:
            supplier_object = Supplier.objects.filter(name=supplier_data).first()
            if not supplier_object:
                raise serializers.ValidationError({"supplier": "تامین‌کننده پیدا نشد."})
            instance.supplier = supplier_object

        # به‌روزرسانی اندازه
        if sizes_data:
            size_object, created = SizeSupplier.objects.get_or_create(name=sizes_data)
            instance.sizes = size_object

        # به‌روزرسانی رنگ
        if colors_data:
            colors_object, created = ColorSupplier.objects.get_or_create(name=colors_data)
            instance.colors = colors_object

        # به‌روزرسانی سایر فیلدها
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



