# Generated by Django 5.1.3 on 2024-12-29 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0003_rename_product_in_supplier_purchaseorderdetails_product_in_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]