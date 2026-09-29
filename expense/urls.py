from django.urls import path
from . import views

app_name = 'expense'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('add/', views.add_item, name='add_item'),
    path('lend/add/', views.add_lend, name='add_lend'),
    path('lend/', views.lend_list_page, name='lend_list'),
    path('lend/<int:lend_id>/edit/', views.edit_lend, name='edit_lend'),
    path('lend/<int:lend_id>/delete/', views.delete_lend, name='delete_lend'),
    path('borrow/add/', views.add_borrow, name='add_borrow'),
    path('borrow/', views.borrow_list_page, name='borrow_list'),
    path('borrow/<int:borrow_id>/edit/', views.edit_borrow, name='edit_borrow'),
    path('borrow/<int:borrow_id>/delete/', views.delete_borrow, name='delete_borrow'),
    path('item/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('monthly/', views.monthly_list_page, name='monthly_list'),
    path('api/monthly-summary/', views.monthly_summary_api, name='monthly_summary_api'),
    path('api/day/<int:year>/<int:month>/<int:day>/', views.day_detail_api, name='day_detail_api'),
]