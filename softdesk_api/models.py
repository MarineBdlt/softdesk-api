from django.db import models
from django.conf import settings
from django.contrib import admin
from django.utils import timezone


class Contributor(models.Model):

    user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributor",
    )
    project_id = models.ForeignKey(
        "softdesk_api.Project", on_delete=models.CASCADE, related_name="project"
    )
    # permission = models.Choices()

    def __str__(self):
        return str(self.user_id)


class ContributorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Contributor, ContributorAdmin)


class Project(models.Model):
    project_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)

    class Type(models.TextChoices):
        BACKEND = "BACK"
        FRONTEND = "FRONT"
        IOS = "IOS"
        ANDROID = "AND"

    type = models.fields.CharField(choices=Type.choices, max_length=5)

    author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="creator"
    )

    def __str__(self):
        return self.title


class ProjectAdmin(admin.ModelAdmin):
    pass


admin.site.register(Project, ProjectAdmin)


class Issue(models.Model):
    # issue_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    desc = models.CharField(max_length=1000)
    project_id = models.ForeignKey(
        "softdesk_api.Project", on_delete=models.CASCADE, related_name="issues"
    )

    class Tag(models.TextChoices):
        BUG = "BUG"
        AMELIORATION = "AC"
        TACHE = "TASK"

    tag = models.fields.CharField(choices=Tag.choices, max_length=5)

    class Priority(models.TextChoices):
        FAIBLE = "F"
        MOYENNE = "M"
        ELEVEE = "E"

    priority = models.fields.CharField(choices=Priority.choices, max_length=5)

    class Status(models.TextChoices):
        TO_DO = "TODO"
        CURRENT = "CUR"
        DONE = "DONE"

    status = models.fields.CharField(choices=Status.choices, max_length=5)

    author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reporter"
    )
    assignee_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignee"
    )
    created_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class IssueAdmin(admin.ModelAdmin):
    pass


admin.site.register(Issue, IssueAdmin)


class Comments(models.Model):

    comment_id = models.IntegerField()
    description = models.CharField(max_length=1000)
    author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author"
    )
    issue_id = models.ForeignKey(
        "softdesk_api.Issue", on_delete=models.CASCADE, related_name="issue_related"
    )
    created_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.comment_id, self.issue_id


class CommentsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Comments, CommentsAdmin)
