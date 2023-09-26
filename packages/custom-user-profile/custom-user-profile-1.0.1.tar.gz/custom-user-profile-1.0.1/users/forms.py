from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row, Submit
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.urls import reverse

from .models import CustomUser

GENDER_CHOICES = (
    ("", "Choose..."),
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
)
CONTACT_CHOICES = (
    ("", "Choose..."),
    ("P", "Phone"),
    ("E", "Email"),
    ("N", "None"),
)


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter First Name"}),
        required=True,
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter Last Name"}),
        required=True,
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "eg. example@example.com"}),
        required=True,
    )
    phone = forms.CharField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "eg. +977-98XXXXXXXX"}),
        required=True,
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=True,
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "eg. Street 1, City"}),
        required=True,
    )
    nationality = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "eg. Nepali"}),
        required=True,
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.TextInput(attrs={"type": "date"}),
        required=True,
    )
    education = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "eg. Bachelors"}),
        required=True,
    )
    contact_mode = forms.ChoiceField(
        label="Contact Mode Preference",
        choices=CONTACT_CHOICES,
        required=True,
    )
    # password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "address",
            "nationality",
            "date_of_birth",
            "education",
            "contact_mode",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.form_tag = False
        # self.helper.form_method = "POST"
        # self.helper.form_action = 'signup'
        # self.helper.form_action = reverse("home")
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Row(
                Column("first_name", prepend_text="@",
                       css_class="form-group col-md-6 mb-0"),
                Column("last_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("date_of_birth", css_class="form-group col-md-6 mb-0"),
                Column(Field("gender", css_class="form-control col-md-6 mb-0")),
                css_class="form-row",
            ),
            Row(
                Column("email", css_class="form-group col-md-6 mb-0"),
                Column("phone", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("nationality", css_class="form-group col-md-6 mb-0"),
                Column("address", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            "education",
            Row(
                Column(Field("contact_mode", css_class="form-control mb-0 col-md-6")),
            ),
            Row(
                Column(Field("password1", css_class="form-control mb-0 col-md-6")),
                Column(Field("password2", css_class="form-control mb-0 col-md-6")),
            ),
            Submit("submit", "Sign Up"),
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        print(email)

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "address",
            "nationality",
            "date_of_birth",
            "education",
            "contact_mode",
            "password",
        )


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            "username",
            "password",
            Submit("submit", "login"),
        )

    username = forms.EmailField(
        label="Username/Email", widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        fields = (
            "username",
            "password",
        )

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        email = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if email and password:
            # Authenticate using the email (username) and password
            self.user_cache = authenticate(username=email, password=password)
            if self.user_cache is None or not self.user_cache.is_active:
                raise forms.ValidationError("Invalid email or password")
        return self.cleaned_data
