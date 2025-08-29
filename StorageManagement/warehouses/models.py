# warehouse/models.py

from django.utils.text import slugify
from django.utils.timezone import now
from django.db import models
from mongoengine import ValidationError

from products.models import ProductProperty
from suppliers.models import Supplier, InventorySupplier

class Warehouse(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    address = models.CharField(max_length=100)
    stablished_date = models.DateField(auto_now_add=True)
    is_full = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug
        super(Warehouse, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    def __str__(self):
        return self.title

class Employee(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    tasks = models.ManyToManyField(Task, through='TaskForEmployee', related_name='employees')
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    national_code = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.last_name}"

class TaskForEmployee(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    was_delivered_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee','task')
    def __str__(self):
        return f'{self.employee} {self.task} {self.was_delivered_at}'





class Inventory(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey(ProductProperty, on_delete=models.CASCADE, related_name="inventories") # foreign key from ProductProperty table in the Product app
    stock = models.IntegerField(null=True,blank=True, default=0)

    class Meta:
        unique_together = ('warehouse', 'product')

    def __str__(self):
        return f'{self.warehouse} - {self.product} - {self.stock}'

class PurchaseOrderFromSupplier(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="orders") # foreign key from Supplier table in the supplier app
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField(auto_now_add=True)
    is_applied_to_warehouse = models.BooleanField(default=False)
    expected_delivery_date = models.DateField()
    total_price_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.supplier_id} - {self.warehouse} '


class PurchaseOrderDetails(models.Model):
    purchase_order_id = models.ForeignKey(PurchaseOrderFromSupplier, on_delete=models.CASCADE, related_name='products')
    product_in_supplier = models.ForeignKey(InventorySupplier, on_delete=models.SET_NULL, related_name="orders", null=True) # foreign key from InventorySupplier table in the Supplier app
    quantity_ordered = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    total_price_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)


    def __str__(self):
        return f'{self.purchase_order_id} - {self.product_in_supplier} - {self.quantity_ordered} '

    def save(self, *args, **kwargs):
        if self.product_in_supplier:
            stock = self.product_in_supplier.stock
            if self.quantity_ordered > stock:
                raise ValidationError('Quantity ordered cannot be greater than stock')

            self.price_per_unit = self.product_in_supplier.price
            self.total_price_item = self.price_per_unit * self.quantity_ordered

        super(PurchaseOrderDetails, self).save(*args, **kwargs)




