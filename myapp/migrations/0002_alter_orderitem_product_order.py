# Generated by Django 4.2.4 on 2023-08-12 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product_order',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
