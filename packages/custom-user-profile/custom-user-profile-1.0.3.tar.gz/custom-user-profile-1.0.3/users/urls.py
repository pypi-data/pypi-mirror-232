from django.urls import path, re_path

from .views import (
    ArchivedUserList,
    MyLoginView,
    SignUp,
    UserDeleteView,
    UserDetailView,
    UserEditView,
    UserListView,
    UserPermanentDelete,
    UserUnDeleteView,
    custom404Handler,
    dashboard,
    user_logout,
)

app_name = "users"

urlpatterns = [
    path("", dashboard, name="home"),
    path("list/", UserListView.as_view(), name="user_list"),
    path("archive/", ArchivedUserList.as_view(), name="archive"),
    path("detail/<pk>/", UserDetailView.as_view(), name="user_detail"),
    path("update/<pk>/", UserEditView.as_view(), name="user_edit"),
    path("delete/<pk>/", UserDeleteView.as_view(), name="user_delete"),
    path("register/", SignUp.as_view(), name="user_register"),
    path("login/", MyLoginView.as_view(), name="user_login"),
    path("logout", user_logout, name="user_logout"),
    path("404/", custom404Handler, name="not_found"),
    path("hard-delete/<pk>", UserPermanentDelete.as_view(), name="hard_delete"),
    path("undo-delete/<pk>", UserUnDeleteView.as_view(), name="undo_delete"),
]
