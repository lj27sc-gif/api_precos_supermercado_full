from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, ProductViewSet, PriceViewSet, compare

router = DefaultRouter()
router.register('stores', StoreViewSet)
router.register('products', ProductViewSet)
router.register('prices', PriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('compare/', compare),
]
