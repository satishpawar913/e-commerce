# Generated by Django 5.1.1 on 2024-09-24 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('mobile', 'Mobiles'), ('m_shirts', 'MShirts'), ('m_tshirt', 'MTShirts'), ('m_jeans', 'MJeans'), ('m_hoodies', 'MHoodies'), ('m_shoes', 'MShoes'), ('w_shirts', 'WShirts'), ('w_tshirt', 'WTShirts'), ('w_jeans', 'WJeans'), ('w_hoodies', 'WHoodies'), ('w_shoes', 'WShoes'), ('laptops', 'Laptop'), ('smartwatch', 'SmartWatch'), ('headphones', 'HeadPhones'), ('refrigerator', 'Refrigerator'), ('camera', 'Camera')], default='mobile', max_length=200),
        ),
    ]
