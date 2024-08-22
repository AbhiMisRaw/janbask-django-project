from django.urls import path
from core import views

urlpatterns = [
    path("users/", views.UserCreateView.as_view(), name="create-user"),
    path("users/<str:user_id>/", views.UserUpdateView.as_view(), name="update-user"),
    path(
        "users/<str:user_id>/deactivate/",
        views.UserDeactivateView.as_view(),
        name="deactivate-user",
    ),
    path(
        "users/<str:user_id>/roles/",
        views.UserRoleView.as_view(),
        name="role-user",
    ),
    path(
        "auth/token/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
]
