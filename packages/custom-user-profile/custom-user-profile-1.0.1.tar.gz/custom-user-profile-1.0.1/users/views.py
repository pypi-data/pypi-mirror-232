from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView

from .forms import CustomAuthenticationForm, CustomUserCreationForm
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
            return redirect("users:home")
        else:
            print("User authentication failed or user is inactive")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("users:home")  # Ensure 'home' is the correct URL name

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
    return render(request, "users/home.html", {"data": "some text based data"})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_logout(request):
    logout(request)
    return redirect("users:user_login")
