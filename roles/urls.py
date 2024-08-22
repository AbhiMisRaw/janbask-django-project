from django.urls import path
from . import views

urlpatterns = [
    path("roles/", views.RoleList.as_view(), name="create-list-role"),
    path("roles/<str:pk>/", views.RoleDetail.as_view(), name="update-role"),
]
