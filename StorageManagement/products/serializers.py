from rest_framework import serializers
from .models import Size,Color,Category,ProductRating,ProductProperty,Product,Comment
from suppliers.models import Supplier,SizeSupplier,ColorSupplier
from users.models import User
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

class CommentSerializer(serializers.ModelSerializer):
    product =
    class Meta:
        fields = ['id', 'product', 'user', 'title', 'text', 'created_date']
        read_only_fields = ['id', 'created_date']

    def validate_product(self,value):
        try:
            Product.objects.get(name=value)
            return value
        except:
            raise serializers.ValidationError("product does not exist")
    def validate_user(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User does not exist.")
        return value






