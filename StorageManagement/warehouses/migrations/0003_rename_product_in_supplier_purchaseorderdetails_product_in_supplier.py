# Generated by Django 5.1.3 on 2024-12-29 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0002_rename_product_in_supplier_purchaseorderdetails_product_in_supplier'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorderdetails',
            old_name='product_in_Supplier',
            new_name='product_in_supplier',
        ),
    ]