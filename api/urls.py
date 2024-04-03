from django.urls import include, path
from rest_framework import routers

from api.views import ItemViewSet, OrderViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('items', ItemViewSet, basename='items')
router_v1.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('api/', include(router_v1.urls)),
]
