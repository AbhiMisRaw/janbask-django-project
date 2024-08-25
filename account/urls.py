from django.urls import path
from account import views

urlpatterns = [
    path(
        "auth/token/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "password/reset/", views.UserForgetPasswordView.as_view(), name="pasword-reset"
    ),
    path(
        "password/recover/<str:token>/",
        views.UserSetPasswordView.as_view(),
        name="pasword-set",
    ),
]
