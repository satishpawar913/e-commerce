# Generated by Django 5.1.1 on 2024-09-13 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_remove_order_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('fashion', 'Fashion'), ('electronics', 'Electronics'), ('mobile', 'Mobile')], default=False, max_length=200),
        ),
    ]
