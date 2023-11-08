from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.schemas.openapi import AutoSchema

from .serializers import CommitteeUpdateReadOnlySerializer, CommitteeUpdateCreateSerializer
from .models import CommitteeUpdate
from apps.authentication.models import OnlineGroup, GroupMember

class CommitteeUpdateViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = CommitteeUpdate.objects.filter()
    schema = AutoSchema(tags=["Committee Updates"])
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        return(
            super()
            .get_queryset()
            # .filter(group__group_id=10)
            .order_by("-created_at")
        )
    
    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return CommitteeUpdateReadOnlySerializer
        if self.action == "create":
            return CommitteeUpdateCreateSerializer

        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        user = request.user
        post_serializer = self.get_serializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)
        data = post_serializer.validated_data
        
        group = get_object_or_404(klass=OnlineGroup, group_id=data.get("group_id"))
        # if not group.exists():
        #     raise NotFound("Fant ikke gruppen du lette etter")

        get_object_or_404(klass=GroupMember, user=user, group=group)
        # if not group_member.exists():
        #     raise NotFound("Fant ikke brukeren din i samme gruppe")

        update = CommitteeUpdate.objects.create(
            content=data.get("content"),
            group=group,
        )

        committee_update_serializer = CommitteeUpdateReadOnlySerializer(update)
        return Response(data=committee_update_serializer.data, status=status.HTTP_201_CREATED)

