from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='prices')
    price = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
