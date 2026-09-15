from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('view/', views.view),
    path('add/', views.add),
]