from smtplib import SMTPException
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin

from .forms import (
    RegisterForm,
    LoginForm,
    ProfileForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm
)
from .translations import translations


def get_language(request):
    """
    Get the language from the request or session.
    - Retrieves the language from the GET parameters or session.
    - Defaults to English if no language is found.
    - Stores the language in the session.
    """
    language = request.GET.get('lang')
    if not language:
        language = request.session.get('language', 'en')
    request.session['language'] = language
    return language


def signupuser(request):
    """
    Handle user registration.
    - If the user is already authenticated, redirect to the home page.
    - If the request method is POST, validate and save the form data.
    - If the form is valid, save the user and redirect to the home page.
    - If the form is invalid, re-render the registration page with errors.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])

    if request.user.is_authenticated:
        return redirect(to='newsapp:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST, language=language)
        if form.is_valid():
            form.save()
            return redirect(to='newsapp:index')
        else:
            return render(
                request, 'users/signup.html',
                context={"form": form, "translations": trans}
            )

    form = RegisterForm(language=language)
    return render(
        request, 'users/signup.html',
        context={"form": form, "translations": trans}
    )


def loginuser(request):
    """
    Handle user login.
    - If the user is already authenticated, redirect to the home page.
    - If the request method is POST, validate the login form.
    - If the form is valid, authenticate and log in the user.
    - If authentication fails, display an error message.
    - If the form is invalid, display form errors.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])

    if request.user.is_authenticated:
        return redirect(to='newsapp:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST, language=language)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, trans['login_success'])
                return redirect(to='newsapp:index')
            else:
                messages.error(
                    request, trans['username_or_password_didnt_match']
                )
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, error)
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LoginForm(language=language)

    return render(
        request, 'users/login.html',
        context={"form": form, "translations": trans}
    )


@login_required
def logoutuser(request):
    """
    Handle user logout.
    - Log out the user and redirect to the home page.
    - Display a success message upon logout.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])

    logout(request)
    messages.success(request, trans['logout_success'])
    request.session['language'] = language  # Save language after exiting
    return redirect(to='newsapp:index')


@login_required
def profile(request):
    """
    Handle user profile.
    - Display and update the user's profile information.
    - If the request method is POST, validate and save the profile form.
    - If the form is valid, save the profile and display a success message.
    - If the form is invalid, re-render the profile page with errors.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])

    if request.method == 'POST':
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if profile_form.is_valid():
            if 'avatar' in request.FILES:
                profile_form.save()
                messages.success(request, trans['profile_update_success'])
                return redirect('users:profile')
            else:
                messages.error(request, trans['no_avatar_selected'])
        else:
            messages.error(request, trans['form_invalid'])

    else:
        profile_form = ProfileForm(instance=request.user.profile)

    return render(
        request, 'users/profile.html',
        context={'profile_form': profile_form, 'translations': trans}
    )


class TranslationsContextMixin(ContextMixin):
    """
    Mixin to add translations to the context.
    - Retrieves the language from the session.
    - Adds translations to the context based on the language.
    """
    def get_context_data(self, **kwargs):
        """
        Add translations to the context.
        - Retrieves the language from the request.
        - Adds translations to the context based on the language.
        """
        context = super().get_context_data(**kwargs)
        language = get_language(self.request)
        context['translations'] = translations.get(language,
                                                   translations['en'])
        return context


class CustomPasswordResetView(
    SuccessMessageMixin,
    TranslationsContextMixin,
    PasswordResetView
):
    """
    Custom password reset view.
    - Uses custom password reset form.
    - Sends password reset email with translations.
    - Displays a success message upon sending the email.
    """
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    subject_template_name = 'users/password_reset_subject.txt'
    form_class = CustomPasswordResetForm

    # def get_success_message(self, cleaned_data):
    #     """
    #     Get the success message for password reset email sent.
    #     - Retrieves the translated success message.
    #     """
    #     language = get_language(self.request)
    #     trans = translations.get(language, translations['en'])
    #     return trans['email_sent'] % {'email': cleaned_data['email']}

    def get_form_kwargs(self):
        """
        Get the form keyword arguments.
        - Adds the language to the form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['language'] = get_language(self.request)
        return kwargs

    def form_valid(self, form):
        """
        Handle a valid form submission.
        - Sends the password reset email.
        - Displays appropriate error messages if email sending fails.
        """
        language = get_language(self.request)
        trans = translations.get(language, translations['en'])
        email = form.cleaned_data['email']
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            try:
                return super().form_valid(form)
            except SMTPException:
                messages.error(self.request, trans['email_send_error'])
                return render(
                    self.request,
                    self.template_name, {'form': form, 'translations': trans}
                )
        else:
            messages.error(self.request, trans['password_reset_no_account'])
            return render(
                self.request,
                self.template_name, {'form': form, 'translations': trans}
            )


class CustomPasswordResetConfirmView(
    SuccessMessageMixin,
    TranslationsContextMixin,
    PasswordResetConfirmView
):
    """
    Custom password reset confirm view.
    - Uses custom set password form.
    - Displays a success message upon successful password reset.
    - Handles token validation and displays error for invalid tokens.
    """
    template_name = 'users/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')

    def get_form_kwargs(self):
        """
        Get the form keyword arguments.
        - Adds the language to the form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['language'] = get_language(self.request)
        return kwargs

    def form_valid(self, form):
        """
        Handle a valid form submission.
        - Displays a success message upon successful password reset.
        """
        # language = get_language(self.request)
        # trans = translations.get(language, translations['en'])
        # messages.success(
        #     self.request, trans['password_reset_complete_message']
        # )
        return super().form_valid(form)


class CustomPasswordResetCompleteView(
    SuccessMessageMixin,
    TranslationsContextMixin,
    PasswordResetCompleteView
):
    """
    Custom password reset complete view.
    - Displays the password reset complete page.
    """
    template_name = 'users/password_reset_complete.html'


class CustomPasswordResetDoneView(
    SuccessMessageMixin,
    TranslationsContextMixin,
    PasswordResetDoneView
):
    """
    Custom password reset done view.
    - Displays the password reset done page.
    """
    template_name = 'users/password_reset_done.html'


def password_reset_request(request):
    """
    Handle password reset request.
    - If the request method is POST, validate and process
      the password reset form.
    - If the form is valid, send the password reset email.
    - If the email sending fails, display an error message.
    - If the email is not associated with any account,
      display an error message.
    - Re-render the password reset page with the form and translations.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])

    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST, language=language)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                try:
                    return CustomPasswordResetView.as_view()(request)
                except SMTPException as err:
                    print(f"SMTP error occurred: {err}")
                    messages.error(
                        request,
                        trans['smtp_error']
                    )
                    return redirect('users:password_reset')
            else:
                messages.error(
                    request,
                    trans['password_reset_no_account']
                )
                return render(
                    request, "users/password_reset.html",
                    {"form": form, "translations": trans}
                )
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomPasswordResetForm(language=language)

    return render(
        request, "users/password_reset.html",
        {"form": form, "translations": trans}
    )
