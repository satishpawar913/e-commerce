from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('mobile', 'Mobiles'),
        ('m_shirts', 'MensShirts'),
        ('m_tshirt', 'MensTShirts'),
        ('m_jeans', 'MensJeans'),
        ('m_hoodies', 'MensHoodies'),
        ('m_shoes', 'MensShoes'),
        ('w_shirts', 'WomenShirts'),
        ('w_tshirt', 'WomenTShirts'),
        ('w_jeans', 'WomenJeans'),
        ('w_hoodies', 'WomenHoodies'),
        ('w_shoes', 'WomenShoes'),
        ('laptops', 'Laptop'),
        ('smartwatch', 'SmartWatch'),
        ('headphones', 'HeadPhones'),
        ('refrigerator', 'Refrigerator'),
        ('camera', 'Camera'),
    )

    name = models.CharField(max_length=200)
    price = models.FloatField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=200, default='mobile')
    brand = models.CharField(max_length=100, null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.brand})"

    def delete(self, *args, **kwargs):
        OrderItem.objects.filter(product=self).delete()
        super().delete(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for item in orderitems:
            if not item.product.digital:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
