from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, UserProfileForm


def register(request):
    try:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! You are now logged in.')
                return redirect('login')
        else:
            form = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {'form': form})
    except Exception as e:
        messages.error(request, f'An error occurred during registration: {str(e)}')
        return redirect('register')


def logout_view(request):
    try:
        logout(request)
        return redirect('store')
    except Exception as e:
        messages.error(request, f'An error occurred while logging out: {str(e)}')
        return redirect('store')


def generate_otp():
    return str(random.randint(100000, 999999))


def login_view(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                otp = generate_otp()
                print("Generated OTP:", otp)
                request.session['otp'] = otp
                request.session['username'] = user.username
                request.session['password'] = request.POST['password']
                messages.success(request, "An OTP has been sent on your console!")
                return redirect('verify-otp')
        else:
            form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})
    except Exception as e:
        messages.error(request, f'An error occurred during login: {str(e)}')
        return redirect('login')


@login_required
def edit_profile(request):
    try:
        user = request.user
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
        else:
            form = UserProfileForm(instance=user)
        return render(request, 'accounts/edit_profile.html', {'form': form})
    except Exception as e:
        messages.error(request, f'An error occurred while editing profile: {str(e)}')
        return redirect('profile')


@login_required
def get_profile(request):
    try:
        return render(request, 'accounts/profile.html')
    except Exception as e:
        messages.error(request, f'An error occurred while fetching profile: {str(e)}')
        return redirect('store')


def verify_otp(request):
    try:
        if request.user.is_authenticated:
            return redirect('store')

        if 'otp' not in request.session:
            return redirect('store')

        if request.method == 'POST':
            entered_otp = request.POST.get('otp')
            stored_otp = request.session.get('otp')

            if entered_otp == stored_otp:
                uname = request.session.get('username')
                upass = request.session.get('password')
                user = authenticate(username=uname, password=upass)

                if user is not None:
                    login(request, user)
                    messages.success(request, "Successfully logged in!")
                    return redirect('store')
                else:
                    messages.error(request, "Authentication failed. User not found.")
            else:
                messages.error(request, "Invalid OTP. Please try again.")

        return render(request, 'accounts/verify_otp.html')
    except Exception as e:
        messages.error(request, f'An error occurred during OTP verification: {str(e)}')
        return redirect('login')


def force_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    elif strings_only and isinstance(s, (list, tuple)):
        return [force_str(item, encoding, strings_only, errors) for item in s]
    return s


def forgot_password(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://localhost:8000/reset-password/{uid}/{token}/"

            send_mail(
                'Password Reset Request',
                render_to_string('accounts/password_reset_email.html', {'reset_link': reset_link}),
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('password_reset_done')
        return render(request, 'accounts/forgot_password.html')
    except User.DoesNotExist:
        messages.error(request, 'Email not found')
        return render(request, 'accounts/forgot_password.html')
    except Exception as e:
        messages.error(request, f'An error occurred during password reset request: {str(e)}')
        return render(request, 'accounts/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            new_password_confirm = request.POST.get('new_password_confirm')
            if new_password == new_password_confirm:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match')

        return render(request, 'accounts/reset_password.html', {'user': user, 'uidb64': uidb64, 'token': token})
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        messages.error(request, f'Invalid reset link: {str(e)}')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred during password reset: {str(e)}')
        return redirect('login')


def password_reset_done_view(request):
    try:
        return render(request, 'accounts/password_reset_done.html')
    except Exception as e:
        messages.error(request, f'An error occurred while displaying the password reset done page: {str(e)}')
        return redirect('store')


@login_required
def change_password(request):
    try:
        if request.method == 'POST':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('login')
        else:
            form = CustomPasswordChangeForm(request.user)

        return render(request, 'accounts/change_password.html', {'form': form})
    except Exception as e:
        messages.error(request, f'An error occurred while changing password: {str(e)}')
        return redirect('change_password')

