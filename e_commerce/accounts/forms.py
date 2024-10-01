from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Role  # Import the Role model


class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for creating a new user with an associated role.

    Inherits from Django's UserCreationForm to extend functionality
    and add an email field and role selection.
    """
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Enter a valid email address.',
        }
    )

    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Seller', 'Seller'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        error_messages={
            'required': 'Please select a role.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
        error_messages = {
            'username': {
                'required': 'Please enter a username.',
                'max_length': 'Username cannot exceed 150 characters.',
            },
            'email': {
                'required': 'Please enter your email address.',
                'invalid': 'Enter a valid email address.',
            },
            'password1': {
                'required': 'Please enter a password.',
                'password_mismatch': 'Passwords do not match.',
            },
            'password2': {
                'required': 'Please confirm your password.',
                'password_mismatch': 'Passwords do not match.',
            },
        }

    def save(self, commit=True):
        """
        Save the user instance and create an associated role.

        Args:
            commit (bool): Whether to save the user instance to the database.

        Returns:
            User: The saved user instance.

        Raises:
            Exception: If there is an error during user creation or role assignment.
        """
        try:
            # Save the User instance
            user = super().save(commit=False)
            user.email = self.cleaned_data['email']

            if commit:
                user.save()
                # Create the associated Role instance
                role = self.cleaned_data['role']
                Role.objects.create(role=role, user=user)

            return user
        except Exception as e:
            raise Exception(f"Error during user creation: {str(e)}")


class SmsCodeForm(forms.Form):
    """
    A form for submitting a verification code via SMS.
    """
    code = forms.CharField(max_length=6, label='Verification Code')


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    A custom form for changing user passwords.

    Inherits from Django's PasswordChangeForm to provide
    user authentication while changing passwords.
    """
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email']


