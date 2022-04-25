from operator import ge
from pydoc import describe
from urllib import request
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from softdesk_api.models import Project, Issue, Contributor, Comments


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["project_id", "title", "description", "type", "author_user_id"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()
    author_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "title",
            "description",
            "type",
            "author_user_id",
            "issues",
        ]

    # POURQUOI GET SEULEMENT L'ID ET PAS L'INSTANCE ?

    def get_author_user_id(self, instance):
        queryset = instance.author_user_id
        serializer = UserSerializer(queryset)
        return serializer.data

    def get_issues(self, instance):
        queryset = Issue.objects.filter(project_id=instance.project_id)
        if queryset:
            serializer = IssueGetListSerializer(queryset, many=True)
            return serializer.data


class ContributorGetSerializer(serializers.ModelSerializer):
    project_id = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ["project_id", "user_id"]

    def get_project_id(self, instance):
        queryset = instance.project_id
        serializer = ProjectDetailSerializer(queryset)
        return serializer.data

    def get_user_id(self, instance):
        queryset = instance.user_id
        serializer = UserSerializer(queryset)
        return serializer.data


class ContributorPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ["user_id"]


class IssueGetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "project_id",
            "title",
            "tag",
        ]


class IssueGetDetailSerializer(serializers.ModelSerializer):
    author_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "project_id",
            "title",
            "desc",
            "tag",
            "priority",
            "status",
            "assignee_user_id",
        ]

    def get_assignee_user_id(self, instance):
        queryset = instance.assignee_user_id
        serializer = UserSerializer(queryset)
        return serializer.data


class IssuePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "title",
            "desc",
            "tag",
            "priority",
            "status",
            "assignee_user_id",
        ]


class IssueGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "project_id",
            "title",
            "desc",
            "tag",
            "priority",
            "status",
            "assignee_user_id",
            "created_time",
        ]

    def get_assignee_user_id(self, instance):
        queryset = instance.assignee_user_id
        serializer = UserSerializer(queryset)
        return serializer.data


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ["comment_id", "description"]


class CommentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = [
            "comment_id",
            "description",
            "author_user_id",
            "issue_id",
            "created_time",
        ]


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()
        return user
