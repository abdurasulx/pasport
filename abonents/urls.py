"""
Abonents app URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Router for ViewSet
router = DefaultRouter()
router.register(r'abonents', views.AbonentViewSet, basename='abonent')

urlpatterns = [
    # ViewSet URLs (CRUD)
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('add-data/', views.add_data, name='add-data'),
    path('get-pinfl/<str:abonent_kod>/', views.get_pinfl, name='get-pinfl'),
    path('get-rasm/<str:abonent_kod>/', views.get_rasm, name='get-rasm'),
]

# Inspector frontend URLs
inspector_patterns = [
    path('login/', views.inspector_login, name='inspector-login'),
    path('logout/', views.inspector_logout, name='inspector-logout'),
    path('', views.inspector_dashboard, name='inspector-dashboard'),
    path('abonents/', views.inspector_abonent_list, name='inspector-abonent-list'),
    path('abonents/add/', views.inspector_abonent_add, name='inspector-abonent-add'),
    path('abonents/<int:pk>/edit/', views.inspector_abonent_edit, name='inspector-abonent-edit'),
    path('abonents/<int:pk>/delete/', views.inspector_abonent_delete, name='inspector-abonent-delete'),
]

# Custom Admin URLs
custom_admin_patterns = [
    path('', views.custom_admin_dashboard, name='custom-admin-dashboard'),
    
    # Tuman CRUD
    path('tumanlar/', views.admin_tuman_list, name='admin-tuman-list'),
    path('tumanlar/add/', views.admin_tuman_add, name='admin-tuman-add'),
    path('tumanlar/<int:pk>/edit/', views.admin_tuman_edit, name='admin-tuman-edit'),
    path('tumanlar/<int:pk>/delete/', views.admin_tuman_delete, name='admin-tuman-delete'),
    
    # Mahalla CRUD
    path('mahallalar/', views.admin_mahalla_list, name='admin-mahalla-list'),
    path('mahallalar/add/', views.admin_mahalla_add, name='admin-mahalla-add'),
    path('mahallalar/<int:pk>/edit/', views.admin_mahalla_edit, name='admin-mahalla-edit'),
    path('mahallalar/<int:pk>/delete/', views.admin_mahalla_delete, name='admin-mahalla-delete'),
    
    # Inspektor CRUD
    path('inspektorlar/', views.admin_inspektor_list, name='admin-inspektor-list'),
    path('inspektorlar/add/', views.admin_inspektor_add, name='admin-inspektor-add'),
    path('inspektorlar/<int:pk>/edit/', views.admin_inspektor_edit, name='admin-inspektor-edit'),
    path('inspektorlar/<int:pk>/delete/', views.admin_inspektor_delete, name='admin-inspektor-delete'),
    path('inspektorlar/<int:pk>/hisobot/', views.admin_inspektor_report, name='admin-inspektor-report'),
    
    # Abonent CRUD
    path('abonentlar/', views.admin_abonent_list, name='admin-abonent-list'),
    path('abonentlar/add/', views.admin_abonent_add, name='admin-abonent-add'),
    path('abonentlar/<int:pk>/edit/', views.admin_abonent_edit, name='admin-abonent-edit'),
    path('abonentlar/<int:pk>/delete/', views.admin_abonent_delete, name='admin-abonent-delete'),
    
    # PINFL Binding
    path('pinfl-boglash/', views.admin_pinfl_binding, name='admin-pinfl-binding'),
    
    # Image fixing
    path('rasmlarni-tuzatish/', views.admin_fix_images, name='admin-fix-images'),
    
    # Daily Reports
    path('hisobot/', views.admin_daily_reports, name='admin-daily-reports'),
]
