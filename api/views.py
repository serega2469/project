from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.serializers import ItemSerializer, OrderSerializer
from api.mixins import CreateListRetrieveMixin
from api.permissions import IsAdminOrReadOnly

from store.models import Item, Order


class ItemViewSet(GenericViewSet, CreateListRetrieveMixin):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (IsAdminOrReadOnly,)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrReadOnly,)
