"""softdesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from softdesk_api.views import (
    SignupView,
    ProjectViewSet,
    IssueViewSet,
    ContributorViewSet,
    CommentViewSet,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register("project", ProjectViewSet, basename="project")

issue_router = routers.NestedSimpleRouter(router, r"project", lookup="project")
issue_router.register("issue", IssueViewSet, basename="issue")

contributor_router = routers.NestedSimpleRouter(router, r"project", lookup="project")
contributor_router.register("contributor", ContributorViewSet, basename="contributor")

comment_router = routers.NestedSimpleRouter(issue_router, r"issue", lookup="issue")
comment_router.register("comment", CommentViewSet, basename="comment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("", include(issue_router.urls)),
    path("", include(contributor_router.urls)),
    path("", include(comment_router.urls)),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]


# FAIRE CONDITION DANS LA VUE -> SI OBJECT ID EXISTE DEJA, NE PAS RECREER
# AUTOMATISER L'AJOUT D'ID DANS LA CREATION DE COMMENT -> ne correspond pas à celui rentré manuellement
# Gestion des erreurs
# Tests
# DOCUMENTATION POSTMAN
