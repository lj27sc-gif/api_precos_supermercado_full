from rest_framework import serializers
from .models import Store, Product, Price

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class PriceSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    store = StoreSerializer()
    class Meta:
        model = Price
        fields = '__all__'
