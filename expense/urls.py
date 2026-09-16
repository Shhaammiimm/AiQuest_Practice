from django.urls import path
from . import views

app_name = 'expense'

urlpatterns = [
    path('add/', views.add_item, name='add_item'),
    path('monthly/', views.monthly_list_page, name='monthly_list'),
    path('api/monthly-summary/', views.monthly_summary_api, name='monthly_summary_api'),
    path('api/day/<int:year>/<int:month>/<int:day>/', views.day_detail_api, name='day_detail_api'),
]