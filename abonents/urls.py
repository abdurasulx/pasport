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
