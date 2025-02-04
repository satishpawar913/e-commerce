# Generated by Django 5.1.1 on 2024-09-23 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_remove_orderitem_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processed', 'Processed'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], default='pending', max_length=20),
        ),
    ]
