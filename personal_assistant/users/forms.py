from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import (
    validate_password,
    get_default_password_validators
)

from .models import Profile
from .translations import translations


class RegisterForm(UserCreationForm):
    """
    Custom user registration form.
    - Initializes the form with translated labels and placeholders.
    - Validates username uniqueness.
    - Validates password confirmation.
    - Provides custom password validation with translated error messages.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize of the registration form.
        - Sets the language and translations.
        - Updates form field attributes with translated placeholders.
        - Updates form field labels with translated text.
        - Updates error messages with translated text.
        """
        self.language = kwargs.pop('language', 'en')
        self.trans = translations.get(self.language, translations['en'])
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': self.trans['enter_username'],
            'class': 'form-control'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': self.trans['enter_email'],
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': self.trans['enter_password'],
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': self.trans['confirm_password'],
            'class': 'form-control'
        })
        self.fields['username'].label = self.trans['username']
        self.fields['email'].label = self.trans['email']
        self.fields['password1'].label = self.trans['password']
        self.fields['password2'].label = self.trans['password_confirmation']

        self.error_messages.update({
            'password_mismatch': self.trans['password_mismatch'],
            'username_exists': self.trans['username_exists'],
        })

    def clean_username(self):
        """
        Validate of the username uniqueness.
        - Checks if a user with the same username already exists.
        - Raises a validation error if the username is already taken.
        - Returns the cleaned username if it is unique.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(self.error_messages['username_exists'])
        return username

    def clean_password2(self):
        """
        Validate password confirmation.
        - Ensures the two password fields match.
        - Raises a validation error if the passwords do not match.
        - Returns the cleaned password confirmation if they match.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch']
            )
        return password2

    def _post_clean(self):
        """
        Perform additional password validation after the form is cleaned.
        - Validates the password using the default password validators.
        - Adds custom error messages for password validation errors.
        """
        super()._post_clean()
        self._validate_custom_password()

    def _validate_custom_password(self):
        """
        Custom password validation.
        - Validates the password using the default password validators.
        - Adds custom error messages for password validation errors.
        """
        password = self.cleaned_data.get('password1')
        if password:
            errors = []
            try:
                validate_password(
                    password, self.instance,
                    password_validators=get_default_password_validators()
                )
            except forms.ValidationError as e:
                for message in e.messages:
                    if 'too short' in message:
                        errors.append(self.trans['password_too_short'])
                    elif 'too common' in message:
                        errors.append(self.trans['password_too_common'])
                    elif 'entirely numeric' in message:
                        errors.append(self.trans['password_entirely_numeric'])
                    else:
                        errors.append(message)
            if errors:
                self.add_error('password1', forms.ValidationError(errors))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    """
    Custom user login form.
    - Initializes the form with translated labels and placeholders.
    - Authenticates the user based on provided credentials.
    - Provides error messages for invalid login attempts and inactive accounts.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the login form.
        - Sets the language and translations.
        - Updates form field attributes with translated placeholders.
        - Updates form field labels with translated text.
        """
        self.language = kwargs.pop('language', 'en')
        self.trans = translations.get(self.language, translations['en'])
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': self.trans['enter_username'],
            'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': self.trans['enter_password'],
        })
        self.fields['username'].label = self.trans['username']
        self.fields['password'].label = self.trans['password']

    def clean(self):
        """
        Validate login credentials.
        - Authenticates the user based on the provided username and password.
        - Raises a validation error if the credentials are invalid
          or the account is inactive.
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.trans['username_or_password_didnt_match'],
                    code='invalid_login',
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.trans['inactive_account'],
                    code='inactive',
                )
        return self.cleaned_data

    def get_user(self):
        """
        Get the authenticated user.
        - Returns the user object if authentication was successful.
        """
        return self.user_cache

    class Meta:
        fields = ['username', 'password']


class ProfileForm(forms.ModelForm):
    """
    Custom user profile form.
    - Handles the avatar upload for the user's profile.
    """
    avatar = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        model = Profile
        fields = ['avatar']

    def clean(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get("avatar")

        if not avatar and not self.instance.pk:
            self.add_error('avatar', "This field is required.")

        return cleaned_data


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom form for setting a new password.
    - Initializes the form with translated labels and placeholders.
    - Validates the new password and its confirmation.
    - Custom password validation with translated error messages.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the set password form.
        - Sets the language and translations.
        - Updates form field attributes with translated placeholders.
        - Updates form field labels with translated text.
        """
        self.language = kwargs.pop('language', 'en')
        self.trans = translations.get(self.language, translations['en'])
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': self.trans['enter_new_password'],
            'class': 'form-control'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': self.trans['confirm_new_password'],
            'class': 'form-control'
        })
        self.fields['new_password1'].label = self.trans['new_password1']
        self.fields['new_password2'].label = self.trans['new_password2']

    def clean_new_password2(self):
        """
        Validate new password confirmation.
        - Ensures the two new password fields match.
        - Raises a validation error if the passwords do not match.
        - Returns the cleaned password confirmation if they match.
        """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.trans['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        """
        Perform additional password validation after the form is cleaned.
        - Validates the password using the default password validators.
        - Adds custom error messages for password validation errors.
        """
        super()._post_clean()
        self._validate_custom_password()

    def _validate_custom_password(self):
        """
        Custom password validation.
        - Validates the password using the default password validators.
        - Adds custom error messages for password validation errors.
        """
        password = self.cleaned_data.get('new_password1')
        if password:
            errors = []
            try:
                validate_password(
                    password, self.user,
                    password_validators=get_default_password_validators()
                )
            except forms.ValidationError as e:
                for message in e.messages:
                    if 'too short' in message:
                        errors.append(self.trans['password_too_short'])
                    elif 'too common' in message:
                        errors.append(self.trans['password_too_common'])
                    elif 'entirely numeric' in message:
                        errors.append(self.trans['password_entirely_numeric'])
                    else:
                        errors.append(message)
            if errors:
                self.add_error('new_password1', forms.ValidationError(errors))


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom form for password reset.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the password reset form.
        - Sets the language and translations.
        - Updates form field attributes with translated placeholders.
        - Updates form field labels with translated text.
        """
        self.language = kwargs.pop('language', 'en')
        self.trans = translations.get(self.language, translations['en'])
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': self.trans['enter_email'],
            'autofocus': True
        })
        self.fields['email'].label = self.trans['email']
