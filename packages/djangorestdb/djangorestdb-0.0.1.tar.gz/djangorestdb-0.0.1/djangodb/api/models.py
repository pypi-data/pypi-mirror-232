from django.db import models
from djangodb.djangodb.user.models import User


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    price = models.IntegerField()


class Cart(models.Model):
    products = models.ManyToManyField(Product, related_name='products')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Order(models.Model):
    products = models.ManyToManyField(Product, )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_price = models.IntegerField(null=True, blank=True)