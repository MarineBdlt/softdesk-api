from http.client import NOT_FOUND
from xml.etree.ElementTree import Comment
from django.contrib.auth import get_user_model
from django.http import request
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
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
from rest_framework import permissions

# rajouter permissions ;)


class SignupView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = serializers.SignupSerializer


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainPairSerializer


# WORK
class IsAuthorInProjectView(permissions.BasePermission):
    def has_permission(self, request, view):
        # if view.action == "create":
        #    return True
        if view.action in ("destroy", "update"):
            try:
                content = Project.objects.get(pk=view.kwargs["pk"])
            except ObjectDoesNotExist:
                return False
            return content.author_user_id == request.user
        return True


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = (IsAuthorInProjectView,)
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
        print(projects)
        return Project.objects.filter(
            Q(project_id__in=projects) | Q(author_user_id=self.request.user.id)
        )

        #  Person.objects.filter(personscore_set__name="Bob").prefetch_related("personscore_set"
        # return Project.objects.filter(
        #     Q(project_id_in=self.request.user.id)
        #     | Q(author_user_id=self.request.user.id)
        # )

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author_user_id=self.request.user)


class ContributorViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Contributor.objects.all()

    serializer_class = serializers.ContributorDetailSerializer
    post_serializer_class = serializers.ContributorListSerializer

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


# WORK
class IsAuthorContributorInIssueView(permissions.BasePermission):
    def has_permission(self, request, view):
        # if view.action in ("list", "retrieve", "create", "destroy", "update"):
        try:
            content = Project.objects.get(pk=view.kwargs["project_pk"])
        except ObjectDoesNotExist:
            return False
        is_contributor = Contributor.objects.filter(
            project_id=view.kwargs["project_pk"]
        ).filter(user_id=request.user.id)
        if content.author_user_id == request.user or len(is_contributor) > 0:
            return True
        return False


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    permission_classes = (IsAuthorContributorInIssueView,)

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


# Seuls les contributeurs peuvent créer (Create) et lire (Read)
# les commentaires relatifs à un problème.
# En outre, ils ne peuvent les actualiser (Update)
# et les supprimer (Delete) que s'ils en sont les auteurs.
class IsAuthorContributorInCommentView(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "create"):
            print("in first if")
            print(request, view.kwargs)
            try:
                print(request, view.kwargs)
                is_contributor = Contributor.objects.filter(
                    project_id=view.kwargs["project_pk"]
                ).filter(user_id=request.user.id)
                print(is_contributor)

            except ObjectDoesNotExist:
                print("Does not exists")
                return False

            if len(is_contributor) > 0:
                return True

        if view.action in ("destroy", "update"):
            ("in second if")
            print(request, view.kwargs)
            try:
                comment = Comments.objects.get(comment_id=view.kwargs["pk"])
            except ObjectDoesNotExist:
                return False
            return comment.author_user_id == request.user
        return False


class CommentViewSet(ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Comments.objects.all()
    permission_classes = (IsAuthorContributorInCommentView,)

    serializer_class = serializers.CommentDetailSerializer
    post_serializer_class = serializers.CommentListSerializer

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
