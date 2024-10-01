from django.db import models
from django.contrib.auth.models import User, AbstractUser

from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    CUSTOMER = 'Customer'
    SELLER = 'Seller'

    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (SELLER, 'Seller'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
