from email import message
from http.client import NOT_FOUND, INTERNAL_SERVER_ERROR, UNAUTHORIZED
from django.contrib.auth import get_user_model
from django.http import request
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
)  # ajouter permission sisAuthenticated

from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from softdesk_api import serializers
from softdesk_api.models import Project, Issue, Comments, Contributor
from django.contrib.auth.models import User
from django.db.models import Q
from softdesk_api import permissions as p


class SignupView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = serializers.SignupSerializer


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainPairSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = (p.IsAuthorInProjectView,)
    http_method_names = ["get", "post", "put", "delete"]

    serializer_class = serializers.ProjectListSerializer
    detail_serializer_class = serializers.ProjectDetailSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        contributors = Contributor.objects.filter(user_id=self.request.user.id)
        projects = contributors.values_list("project_id")
        return Project.objects.filter(
            Q(id__in=projects) | Q(author_user_id=self.request.user.id)
        )

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author_user_id=self.request.user)


class ContributorViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = (p.IsAuthorInContributorView,)
    queryset = Contributor.objects.all()

    serializer_class = serializers.ContributorDetailSerializer
    list_serializer_class = serializers.ContributorListSerializer

    def get_serializer_class(self):
        if self.action in ("list", "create", "update"):
            return self.list_serializer_class
        return super().get_serializer_class()

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise Exception("A project with this id does not exist.")
        return self.queryset.filter(project_id=project.id)

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        user = get_object_or_404(User, pk=self.request.GET["user_id"])
        if self.queryset.filter(project_id=project, user_id=user).exists():
            raise Exception(
                "This contribution already exists (%s: %s)." % (project, user)
            )
        else:
            serializer.save(project_id=project, user_id=user)


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    permission_classes = (p.IsAuthorContributorInIssueView,)

    serializer_class = serializers.IssueGetListSerializer
    detail_serializer_class = serializers.IssueGetDetailSerializer
    post_serializer_class = serializers.IssuePostSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return self.post_serializer_class
        else:
            if self.action == "retrieve":
                return self.detail_serializer_class
        return super().get_serializer_class()

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise NOT_FOUND("A project with this id does not exist")
        return self.queryset.filter(project_id=project.id)
        # remplacer par get_objects_404

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        serializer.save(
            author_user_id=self.request.user,
            project_id=project,
        )

    def perform_update(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        serializer.save(
            author_user_id=self.request.user,
            project_id=project,
        )


class CommentViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Comments.objects.all()
    permission_classes = (p.IsAuthorContributorInCommentView,)

    serializer_class = serializers.CommentDetailSerializer
    post_serializer_class = serializers.CommentListSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return self.post_serializer_class
        return super().get_serializer_class()

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs["issue_pk"])
        serializer.save(
            author_user_id=self.request.user,
            issue_id=issue,
        )
