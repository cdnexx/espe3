from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from department import views

department_patterns = [
    path('department_add', views.department_add,name="department_add"),



    path('department_list_active', views.department_list_active,name="department_list_active"),
    path('department_list_active/<page>/', views.department_list_active,name="department_list_active"),
    path('department_block/<department_id>/', views.department_block,name="department_block"),
    path('department_activate/<department_id>/', views.department_activate,name="department_activate"),
    path('department_list_deactive', views.department_list_deactive,name="department_list_deactive"),
    path('department_list_deactive/<page>/', views.department_list_deactive,name="department_list_deactive"),
    path('department_edit/<department_id>/', views.department_edit,name="department_edit"),
    path('department_edit_save/', views.department_edit_save,name="department_edit_save"),

    #NUEVOS
    path('department_main/', views.department_main,name="department_main"),
    path('department_view/<request_id>/', views.department_view,name="department_view"),
    path('department_in_progress/', views.department_in_progress,name="department_in_progress"),
    path('department_finish/', views.department_finish,name="department_finish"),
    path('department_view_profile/', views.department_view_profile,name="department_view_profile"),
    path('aceptar_solicitud/', views.aceptar_solicitud, name='aceptar_solicitud')
]  