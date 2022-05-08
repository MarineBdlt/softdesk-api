from django.core.exceptions import ObjectDoesNotExist
from softdesk_api.models import Project, Comments, Contributor
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


class IsAuthorContributorInIssueView(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            project = Project.objects.get(pk=view.kwargs["project_pk"])
        except ObjectDoesNotExist:
            return False
        is_contributor = Contributor.objects.filter(
            project_id=view.kwargs["project_pk"]
        ).filter(user_id=request.user.id)
        if project.author_user_id == request.user or bool(is_contributor):
            return True
        return False


class IsAuthorContributorInCommentView(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "create"):
            try:
                project = Project.objects.get(project_id=view.kwargs["project_pk"])
            except ObjectDoesNotExist:
                print("Does not exists")
                return False
            is_contributor = Contributor.objects.filter(
                project_id=view.kwargs["project_pk"]
            ).filter(user_id=request.user.id)

            if project.author_user_id == request.user or bool(is_contributor):
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
