from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Store, Product, Price
from .serializers import StoreSerializer, ProductSerializer, PriceSerializer
from django.db.models import Min

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.select_related('product','store').all()
    serializer_class = PriceSerializer

@api_view(['GET'])
def compare(request):
    # ?product=nome or id
    q = request.GET.get('product')
    if not q:
        return Response({'error':'product query param required'}, status=400)
    products = Product.objects.filter(name__icontains=q)[:5]
    results = []
    for p in products:
        best = p.prices.aggregate(min_price=Min('price'))
        results.append({'product':p.name,'min_price':best['min_price']})
    return Response(results)
