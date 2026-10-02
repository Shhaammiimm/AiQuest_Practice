

from django.contrib.auth import views as autht_views
from django.urls import path

from accounts import views


app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', autht_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', autht_views.LogoutView.as_view(), name='logout'),
]