# Generated by Django 5.1.1 on 2024-09-13 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_role_role'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Customer',
        ),
    ]
