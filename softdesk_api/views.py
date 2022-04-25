from http.client import NOT_FOUND
from django.contrib.auth import get_user_model
from django.http import request
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from softdesk_api.models import Project, Issue, Comments, Contributor
from django.contrib.auth.models import User
from django.db.models import Q
from softdesk_api import serializers

# rajouter permissions ;)


class SignupView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = serializers.SignupSerializer


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainPairSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    # permission_classes = (AllowAny,)
    http_method_names = ["get", "post", "put", "delete"]

    serializer_class = serializers.ProjectListSerializer
    detail_serializer_class = serializers.ProjectDetailSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        contributors = Contributor.objects.filter(user_id=self.request.user.id)
        return Project.objects.filter(
            Q(author_user_id__in=contributors.values_list("user_id"))
            | Q(author_user_id=self.request.user.id)
        )

    # A TESTER

    # OU CONTRIBUTOR -> REGARDER SI PAIR PROJET- USER DANS TABLE CONTRIBUTOR
    # SI PAIR PROJET -USER DANS CLASS CONTRIBUTOR
    # FILTRER LES PROJETS AVEC AUTHOR_USER_ID = USER_ID DE CONTRIBUTOR
    # UTILISER L'ORM __
    # Q pour OU

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author_user_id=self.request.user)


class ContributorViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Contributor.objects.all()

    serializer_class = serializers.ContributorGetSerializer
    post_serializer_class = serializers.ContributorPostSerializer

    def get_serializer_class(self):
        if self.action in ("create", "uptdate"):
            return self.post_serializer_class
        return super().get_serializer_class()

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            raise NOT_FOUND("A project with this id does not exist")
        return self.queryset.filter(project_id=project.project_id)

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        serializer.save(
            project_id=project,
        )


class IssueViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Issue.objects.all()

    serializer_class = serializers.IssueGetListSerializer
    detail_serializer_class = serializers.IssueGetDetailSerializer
    post_serializer_class = serializers.IssuePostSerializer

    def get_serializer_class(self):
        if self.action in ("create", "uptdate"):
            return self.post_serializer_class
        else:
            if self.action == "retrieve":
                return self.detail_serializer_class
        return super().get_serializer_class()

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            raise NOT_FOUND("A project with this id does not exist")
        return self.queryset.filter(project_id=project.project_id)
        # remplacer par get_objects_404

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        serializer.save(
            author_user_id=self.request.user,
            project_id=project,
        )

    def perform_update(self, serializer):
        serializer.save(
            author_user_id=self.request.user,
            project_id=self.kwargs["project_pk"],
        )


class CommentViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Comments.objects.all()

    serializer_class = serializers.CommentGetSerializer
    post_serializer_class = serializers.CommentPostSerializer

    def get_serializer_class(self):
        if self.action in ("create", "uptdate"):
            return self.post_serializer_class
        return super().get_serializer_class()

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs["issue_pk"])
        serializer.save(
            author_user_id=self.request.user,
            issue_id=issue,
        )

    # comment_id = models.IntegerField()
    # description = models.CharField(max_length=1000)
    # author_user_id = models.ForeignKey(
    #     to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author"
    # )
    # issue_id = models.ForeignKey(
    #     "softdesk_api.Issue", on_delete=models.CASCADE, related_name="issue_related"
    # )
    # created_time = models.DateTimeField(default=timezone.now)
