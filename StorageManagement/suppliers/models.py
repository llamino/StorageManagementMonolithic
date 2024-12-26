from django.db import models


class SizeSupplier(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    def __str__(self):
        return self.name

class ColorSupplier(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    def __str__(self):
        return self.name


class CategorySupplier(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    def __str__(self):
        return self.name
# Create your models here.
class ProductDetailSupplier(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField()
    categories = models.ManyToManyField(CategorySupplier, related_name='products')
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    stablished_date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class InventorySupplier(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetailSupplier, on_delete=models.CASCADE)
    stock = models.IntegerField()
    colors = models.ForeignKey(ColorSupplier, on_delete=models.RESTRICT, null=True, blank=True)
    sizes = models.ForeignKey(SizeSupplier, on_delete=models.RESTRICT, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    price = models.IntegerField()
    def __str__(self):
        return f'{self.supplier} - {self.product} - {self.stock}'