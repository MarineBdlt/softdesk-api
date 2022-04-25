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

# 1 - UNE INSCRIPTION QUI FONCTIONNE
# voir comment s'identifier avec jwt : créer un endpoint pour signup : un serializer, une view pour faire une requete post genericApiView
# la methode register avec appeler le serializer, une fois que c'est fait -> save, set_password qui permet d'hacher le mot de passe

# 2 - LOGIN ET RECUP TOKEN

# 3 - ROUTER DE PROJECT
# quelles sont les données qu'on demande et qu'on remplies automatiquement ?
# faire router, l'ajouter dans les urls, models viewset avec le CRUD juste pour projet pour commencer

# permissions, QUI A LE DROIT DE FAIRE QUOI ?
# 1. Author, 2. Contributor, 3. Anonyme

# Ici nous créons notre routeur

# Puis lui déclarons une url basée sur le mot clé ‘category’ et notre view
# afin que l’url générée soit celle que nous souhaitons ‘/api/category/’
# router = routers.SimpleRouter()
# router.register("signup", SignupAPIView, basename="signup")

router = routers.SimpleRouter()
router.register("project", ProjectViewSet, basename="project")

issue_router = routers.NestedSimpleRouter(router, r"project", lookup="project")
issue_router.register("issue", IssueViewSet, basename="issue")

contributor_router = routers.NestedSimpleRouter(router, r"project", lookup="project")
contributor_router.register("contributor", ContributorViewSet, basename="contributor")

comment_router = routers.NestedSimpleRouter(issue_router, r"issue", lookup="issue")
contributor_router.register("comment", CommentViewSet, basename="comment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path("api/", include(issue_router.urls)),
    path("api/", include(contributor_router.urls)),
    path("api/signup/", SignupView.as_view(), name="signup"),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path(
    #     r"^project/(?P<project_pk>\d+)/issue/?$",
    #     IssueViewSet.as_view({"get": "list"}),
    #     name="library-book-list",
    # ),
]

# from rest_framework_nested import routersrouter = SimpleRouter()

# path(r'^project/(?P<project_pk>\d+)/issue/?$', IssueViewSet.as_view(), name='library-book-list')# Pourquoi ne pas les mettre dans le router ?
# router.register('libraries', views.LibraryViewSet)book_router = routers.NestedSimpleRouter(
#     router,
#     r'libraries',
#     lookup='library')book_router.register(
#     r'books',
#     views.BookViewSet,
#     basename='library-book'
# )app_name = 'library'urlpatterns = [
#     path('', include(router.urls)),
#     path('', include(book_router.urls)),
# ]


# path(
#     "ticket-detail/<int:ticket_id>",
#     flux.views.ticket_detail,
#     name="ticket_detail"
# ),
