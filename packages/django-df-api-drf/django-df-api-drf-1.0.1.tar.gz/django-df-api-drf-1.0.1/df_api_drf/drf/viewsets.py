from django.db.models import QuerySet
from rest_framework.viewsets import ModelViewSet

from df_api_drf.drf.permissions import IsOwner


class ModelOwnerViewSet(ModelViewSet):
    permission_classes = (IsOwner,)

    def get_queryset(self) -> QuerySet:
        user_attribute = getattr(self.queryset.model, "user_attribute", "user")
        return (
            self.queryset.filter(**{user_attribute: self.request.user})
            if self.request.user.is_authenticated
            else self.queryset.none()
        )
