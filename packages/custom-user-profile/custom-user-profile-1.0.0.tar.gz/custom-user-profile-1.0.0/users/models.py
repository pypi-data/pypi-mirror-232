from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager

# Backward compatible with django 3.x
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    )
    CONTACT_CHOICES = (
        ("P", "Phone"),
        ("E", "Email"),
        ("N", "None"),
    )

    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    gender = models.CharField(
        _("Gender"), max_length=50, choices=GENDER_CHOICES)
    phone = models.CharField(_("Phone"), max_length=50)
    email = models.EmailField(_("Email Address"), unique=True, max_length=254)
    address = models.CharField(_("Address"), max_length=254)
    nationality = models.CharField(_("Nationality"), max_length=50)
    date_of_birth = models.DateField(
        _("Date of Birth"), auto_now=False, auto_now_add=False, blank=True, null=True)
    education = models.CharField(_("Education Background"), max_length=50)
    contact_mode = models.CharField(
        _("Prefered Contact Mode"), max_length=50, choices=CONTACT_CHOICES)
    is_admin = models.BooleanField(_("Admin"), default=False)
    archive = models.BooleanField(_("Archive"), default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} || {self.email}"
