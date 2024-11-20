from django.urls import path
from core import views

core_urlpatterns = [
    path('', views.home, name='home'),
    path('check_group_main', views.check_group_main, name='check_group_main'),   
    path('landing',views.landing_page,name='landing'),
    path('inicio',views.inicio,name='inicio'),

    path('dashboard_admin',views.dashboard_admin,name='dashboard_admin'),
    path('territorial_main',views.territorial_main,name='territorial_main'),
    path('departamento_main',views.departamento_main,name='departamento_main'),
    path('dirección_main',views.dirección_main,name='dirección_main'),
    path('cuadrilla_main',views.cuadrilla_main,name='cuadrilla_main'),                
]
