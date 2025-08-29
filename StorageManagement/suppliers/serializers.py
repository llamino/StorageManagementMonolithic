from rest_framework import serializers
from .models import CategorySupplier,SizeSupplier,ColorSupplier,ProductDetailSupplier,InventorySupplier,Supplier


# ===================================================================================================================================================


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('name','phone_number','address','is_active')


# ===================================================================================================================================================


class CategorySupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySupplier
        fields = ('name',)


# ===================================================================================================================================================


class SizeSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeSupplier
        fields = ('name',)


# ===================================================================================================================================================


class ColorSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorSupplier
        fields = ('name',)


# ===================================================================================================================================================


class CategorySupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategorySupplier
        fields = ('name',)
        extra_kwargs = {
            'name': {'validators': []}  # حذف validators
        }
# ===================================================================================================================================================


class ProductDetailSupplierSerializer(serializers.ModelSerializer):
    categories = CategorySupplierSerializer(many=True)  # سریالایزر برای دسته‌بندی‌ها

    class Meta:
        model = ProductDetailSupplier
        fields = ['name', 'description', 'categories', 'created_date']

    def create(self, validated_data):
        # استخراج دسته‌بندی‌ها از داده‌های معتبر
        categories_data = validated_data.pop('categories', [])

        # ایجاد محصول جدید
        product = ProductDetailSupplier.objects.create(**validated_data)
        categories = []
        for category_data in categories_data:
            category_name = category_data.get('name')  # استخراج نام دسته‌بندی
            category, created = CategorySupplier.objects.get_or_create(name=category_name)
            categories.append(category)
            # اضافه کردن دسته‌بندی به محصول
        product.categories.set(categories)

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
            existing_categories = CategorySupplier.objects.filter(name__in=unique_categories)
            existing_category_names = set(cat.name for cat in existing_categories)

            new_categories = [
                CategorySupplier(name=name) for name in unique_categories if name not in existing_category_names
            ]
            CategorySupplier.objects.bulk_create(new_categories)

            # تنظیم دسته‌بندی‌ها برای محصول
            all_categories = CategorySupplier.objects.filter(name__in=unique_categories)
            instance.categories.set(all_categories)

        return instance


# ===================================================================================================================================================


class InventorySupplierSerializer(serializers.ModelSerializer):
    size = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    color = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    supplier = serializers.CharField(required=True)

    class Meta:
        model = InventorySupplier
        fields = ('id', 'supplier', 'product', 'stock', 'color', 'size', 'weight', 'price')

    def create(self, validated_data):
        # استخراج داده‌ها
        supplier_data = validated_data.pop('supplier', None)
        size_data = validated_data.pop('size', None)
        color_data = validated_data.pop('color', None)

        # بررسی اینکه supplier حتما وارد شده باشد
        if not supplier_data:
            raise serializers.ValidationError({"supplier": "اطلاعات تامین‌کننده الزامی است."})

        # گرفتن یا ایجاد اشیاء
        supplier_object, created = Supplier.objects.get_or_create(name=supplier_data)

        size_object = None
        if size_data:
            size_object, created = SizeSupplier.objects.get_or_create(name=size_data)

        color_object = None
        if color_data:
            color_object, created = ColorSupplier.objects.get_or_create(name=color_data)

        # ایجاد نمونه جدید
        instance = InventorySupplier.objects.create(
            supplier=supplier_object,
            size=size_object,
            color=color_object,
            **validated_data
        )
        return instance

    def update(self, instance, validated_data):
        # استخراج داده‌ها
        supplier_data = validated_data.pop('supplier', None)
        size_data = validated_data.pop('size', None)
        color_data = validated_data.pop('color', None)

        # به‌روزرسانی تامین‌کننده
        if supplier_data:
            supplier_object = Supplier.objects.filter(name=supplier_data).first()
            if not supplier_object:
                raise serializers.ValidationError({"supplier": "تامین‌کننده پیدا نشد."})
            instance.supplier = supplier_object

        # به‌روزرسانی اندازه
        if size_data:
            size_object, created = SizeSupplier.objects.get_or_create(name=size_data)
            instance.size = size_object
        elif size_data == '' or size_data is None:
            instance.size = None

        # به‌روزرسانی رنگ
        if color_data:
            color_object, created = ColorSupplier.objects.get_or_create(name=color_data)
            instance.color = color_object
        elif color_data == '' or color_data is None:
            instance.color = None

        # به‌روزرسانی سایر فیلدها
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


