# Generated by Django 5.1.3 on 2024-12-31 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0006_alter_purchaseorderdetails_product_in_supplier_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorderdetails',
            old_name='purchase_order_from_supplier',
            new_name='purchase_order_id',
        ),
        migrations.RenameField(
            model_name='purchaseorderdetails',
            old_name='total_price',
            new_name='total_price_item',
        ),
        migrations.RenameField(
            model_name='purchaseorderfromsupplier',
            old_name='total_price',
            new_name='total_price_order',
        ),
        migrations.AddField(
            model_name='purchaseorderfromsupplier',
            name='is_apply_to_inventory',
            field=models.BooleanField(default=False),
        ),
    ]
