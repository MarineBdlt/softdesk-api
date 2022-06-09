from django.core.exceptions import ObjectDoesNotExist
from softdesk_api.models import Issue, Project, Comments, Contributor
from rest_framework import permissions


class IsAuthorInProjectView(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("destroy", "update"):
            try:
                content = Project.objects.get(pk=view.kwargs["pk"])
            except ObjectDoesNotExist:
                return False
            return content.author_user_id == request.user
        return True


class IsAuthorInContributorView(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("destroy", "update"):
            try:
                content = Project.objects.get(pk=view.kwargs["project_pk"])
            except ObjectDoesNotExist:
                return False
            return content.author_user_id == request.user
        return True


class IsAuthorContributorInIssueView(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "create"):
            try:
                project = Project.objects.get(id=view.kwargs["project_pk"])
            except ObjectDoesNotExist:
                return False
            is_contributor = Contributor.objects.filter(
                project_id=view.kwargs["project_pk"]
            ).filter(user_id=request.user.id)
            if project.author_user_id == request.user or bool(is_contributor):
                return True
            return False
        if view.action in ("destroy", "update"):
            try:
                issue = Issue.objects.get(id=view.kwargs["pk"])
            except ObjectDoesNotExist:
                return False
            return issue.author_user_id == request.user


class IsAuthorContributorInCommentView(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "create"):
            try:
                project = Project.objects.get(id=view.kwargs["project_pk"])
            except ObjectDoesNotExist:
                return False
            is_contributor = Contributor.objects.filter(
                project_id=view.kwargs["project_pk"]
            ).filter(user_id=request.user.id)

            if project.author_user_id == request.user or bool(is_contributor):
                return True

        if view.action in ("destroy", "update"):
            try:
                comment = Comments.objects.get(id=view.kwargs["pk"])
            except ObjectDoesNotExist:
                return False
            return comment.author_user_id == request.user
        return False
