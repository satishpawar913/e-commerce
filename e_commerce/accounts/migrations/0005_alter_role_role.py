# Generated by Django 5.1.1 on 2024-09-13 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.CharField(choices=[('Customer', 'Customer'), ('Seller', 'Seller')], max_length=10),
        ),
    ]
