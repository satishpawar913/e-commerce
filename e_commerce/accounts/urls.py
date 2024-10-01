from django.urls import path
from . import views
from .views import forgot_password, reset_password, password_reset_done_view, change_password, get_profile

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset-password'),
    path('password-reset-done/', password_reset_done_view, name='password_reset_done'),
    path('change-password/', change_password, name='change-password'),

    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('profile/', get_profile, name='profile'),

]
