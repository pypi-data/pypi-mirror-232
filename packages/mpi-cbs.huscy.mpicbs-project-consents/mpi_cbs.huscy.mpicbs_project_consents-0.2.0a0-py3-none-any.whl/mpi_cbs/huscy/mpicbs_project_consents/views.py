from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField
from rest_framework.viewsets import GenericViewSet

from huscy.projects.models import Project
from huscy.projects.permissions import IsProjectMember
from huscy.project_consents import models, permissions, serializer
from mpi_cbs.huscy.subjects_wrapper.models import WrappedSubject


class MPICBSProjectConsentTokenSerializer(serializer.ProjectConsentTokenSerializer):
    subject = CharField()

    class Meta:
        model = models.ProjectConsentToken
        fields = 'id', 'created_at', 'created_by', 'project', 'subject'
        read_only_fields = 'project',

    def validate_subject(self, pseudonym):
        try:
            wrapped_subject = WrappedSubject.objects.get(pseudonym=pseudonym)
        except WrappedSubject.DoesNotExist:
            raise ValidationError('Subject does not exist')
        return wrapped_subject.subject


class MPICBSProjectConsentTokenViewSet(CreateModelMixin, GenericViewSet):
    queryset = models.ProjectConsentToken.objects
    permission_classes = (
        IsAuthenticated,
        permissions.HasCreateProjectConsentTokenPermission | IsProjectMember,
    )
    serializer_class = MPICBSProjectConsentTokenSerializer

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(project=self.project)
