from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   RetrieveModelMixin,
                                   UpdateModelMixin)


class CreateListRetrieveMixin(CreateModelMixin,
                              RetrieveModelMixin,
                              UpdateModelMixin,
                              ListModelMixin):
    pass
