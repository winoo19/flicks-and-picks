"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include


# from rest_framework.routers import DefaultRouter
from apps.users.views import (
    UserRegisterView,
    UserLoginView,
    UserProfileInfoView,
    UserProfileUpdateView,
    UserLogoutView,
    UserDeleteView,
    PostReviewView,
    RetrieveReviewsView,
    DeleteReviewView,
    FilterFilmsView,
    FilmDetailView,
    FilmReviewsView,
    AggregateDirectorView,
    AggregateActorView,
    AggregateFilmView,
    DeleteDirectorView,
    DeleteActorView,
    DeleteFilmView,
)

user_urls: list[path] = [
    path("users/register/", UserRegisterView.as_view(), name="user_register"),
    path("users/login/", UserLoginView.as_view(), name="user_login"),
    path("users/profile-info/", UserProfileInfoView.as_view(), name="user_info"),
    path("users/profile-update/", UserProfileUpdateView.as_view(), name="user_update"),
    path("users/logout/", UserLogoutView.as_view(), name="user_logout"),
    path("users/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("users/add-review/", PostReviewView.as_view(), name="user_add_review"),
    path("users/delete-review/", DeleteReviewView.as_view(), name="user_del_review"),
    path("users/history/", RetrieveReviewsView.as_view(), name="user_history"),
]

site_urls: list[path] = [
    path("films/", FilterFilmsView.as_view(), name="film_filter"),
    path("films/<int:id>/", FilmDetailView.as_view(), name="film_info"),
    path("films/<int:id>/reviews/", FilmReviewsView.as_view(), name="film_reviews"),
]

admin_urls: list[path] = [
    path("admin/", admin.site.urls),
    path("site-admin/add-director/", AggregateDirectorView.as_view(), name="add_dir"),
    path("site-admin/add-actor/", AggregateActorView.as_view(), name="add_actor"),
    path("site-admin/add-film/", AggregateFilmView.as_view(), name="add_film"),
    path("site-admin/delete-director/", DeleteDirectorView.as_view(), name="del_dir"),
    path("site-admin/delete-actor/", DeleteActorView.as_view(), name="del_actor"),
    path("site-admin/delete-film/", DeleteFilmView.as_view(), name="del_film"),
]

debug_urls: list[path] = [
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns: list[path] = [
    *user_urls,
    *site_urls,
    *admin_urls,
    *debug_urls,
]
