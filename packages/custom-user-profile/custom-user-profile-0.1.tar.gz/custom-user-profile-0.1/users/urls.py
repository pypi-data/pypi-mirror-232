from django.urls import path

from .views import MyLoginView, SignUp, dashboard, user_logout

app_name = "users"

urlpatterns = [
    path("register/", SignUp.as_view(), name="user_register"),
    path("login/", MyLoginView.as_view(), name="user_login"),
    path("", dashboard, name="home"),
    path("logout", user_logout, name="user_logout"),
]
