# Generated by Django 4.2.2 on 2023-07-02 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_cart_cartitems'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitems',
            name='quantity',
        ),
    ]