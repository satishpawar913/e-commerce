from django.contrib import admin

from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','price','brand','category','digital','image']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','date_ordered','complete','transaction_id']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user','product','order','quantity','date_added','status']


@admin.register(ShippingAddress)
class ShippingAddAdmin(admin.ModelAdmin):
    list_display = ['user','order','address','city','state','zipcode']
