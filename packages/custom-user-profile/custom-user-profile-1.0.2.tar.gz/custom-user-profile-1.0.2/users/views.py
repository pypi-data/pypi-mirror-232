from typing import Any

from django import http
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView

from .forms import CustomAuthenticationForm, CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class MyLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "users/login.html"
    # success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.user_cache
        print(user)

        if user and user.is_active:
            print("Authenticated user:", user)
            print("Redirecting to 'home'")
            login(self.request, user)
            return redirect("home")
        else:
            print("User authentication failed or user is inactive")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("home")  # Ensure 'home' is the correct URL name

    def form_invalid(self, form):
        print("Form is invalid")  # Check if this is called for invalid forms
        print(form.user_cache)
        return super().form_invalid(form)


class SignUp(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/create.html"
    success_url = reverse_lazy("users:user_login")

    def form_valid(self, form):
        form.instance.username = form.cleaned_data["email"]
        return super().form_valid(form)


def dashboard(request):
    return render(request, "users/home.html", {"data": "This is the home page for custom user data"})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_logout(request):
    logout(request)
    return redirect("users:user_login")


class UserListView(ListView):
    queryset = CustomUser.objects.filter(archive=False).order_by("-date_joined")
    model = CustomUser
    context_object_name = "users_list"
    template_name = "users/user_list.html"


class ArchivedUserList(ListView):
    queryset = CustomUser.objects.filter(archive=True).order_by("-date_joined")
    model = CustomUser
    context_object_name = "users_list"
    template_name = "users/user_list.html"


class UserDetailView(DetailView):
    model = CustomUser
    template_name = "users/user_detail.html"
    # queryset = CustomUser.objects.filter(archive=False)

    def get_object(self, queryset=None):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(CustomUser, id=user_id, archive=False)
        return user


class UserEditView(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "users/user_edit.html"
    success_url = reverse_lazy("home")


class UserDeleteView(View):
    model = CustomUser
    template_name = "users/user_delete.html"

    def get(self, request, pk, **kwargs):
        object = get_object_or_404(CustomUser, id=pk)
        object.soft_delete(archive=True)
        return redirect(request.META.get("HTTP_REFERER"))


class UserUnDeleteView(View):
    model = CustomUser
    template_name = "users/user_delete.html"

    def get(self, request, pk, **kwargs):
        object = get_object_or_404(CustomUser, id=pk)
        object.soft_delete(archive=False)
        return redirect(request.META.get("HTTP_REFERER"))


class UserPermanentDelete(DeleteView):
    model = CustomUser

    def get_success_url(self) -> str:
        return self.request.META.get("HTTP_REFERER")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            handler = getattr(self, "delete")
            return handler(request, *args, **kwargs)


def custom404Handler(request, exception, template_name="users/404.html"):
    response = render(request, template_name)
    response.status_code = 400
    return response
