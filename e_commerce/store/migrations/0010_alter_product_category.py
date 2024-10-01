# Generated by Django 5.1.1 on 2024-09-20 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_orderitem_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('mobile', 'Mobiles'), ('shirts', 'Shirts'), ('tshirt', 'TShirts'), ('jeans', 'Jeans'), ('hoodies', 'Hoodies'), ('shoes', 'Shoes'), ('laptops', 'Laptop'), ('smartwatch', 'SmartWatch'), ('headphones', 'HeadPhones')], default=False, max_length=200),
        ),
    ]
