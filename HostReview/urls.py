from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scan/<int:profile_id>/', views.scan_system, name='scan_system'),
    path('results/<int:profile_id>/', views.scan_results, name='scan_results'),
    path('delete/<int:profile_id>/', views.delete_profile, name='delete_profile'),
    path('ajax/scan/', views.ajax_scan_system, name='ajax_scan_system'),
    path('ajax/check_scan_status/', views.ajax_check_scan_status, name='ajax_check_scan_status'),
]
