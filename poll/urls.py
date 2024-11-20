from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from poll import views


poll_patterns = [
    path('poll_main/', views.poll_main,name="poll_main"),
    path('poll_main/<page>/', views.poll_main,name="poll_main"),
    path('poll_add', views.poll_add,name="poll_add"),

    path('poll_fields_delete/<poll_id>/<field>/', views.poll_fields_delete,name="poll_fields_delete"),
    path('poll_add_end/', views.poll_add_end,name="poll_add_end"),
    path('poll_edit_end/', views.poll_edit_end,name="poll_edit_end"),



    path('poll_view/<poll_id>/', views.poll_view,name="poll_view"),
    path('poll_block/<poll_id>/', views.poll_block,name="poll_block"),
    path('poll_activate/<poll_id>/', views.poll_activate,name="poll_activate"),
    path('poll_edit/<poll_id>/', views.poll_edit,name="poll_edit"),
    path('poll_list_create/<page>/', views.poll_list_create,name="poll_list_create"),
    path('poll_list_create', views.poll_list_create,name="poll_list_create"),
    path('poll_list_deactivate/<page>/', views.poll_list_deactivate,name="poll_list_deactivate"),
    path('poll_list_deactivate', views.poll_list_deactivate,name="poll_list_deactivate"),

    path('poll_add_field/<poll_id>/', views.poll_add_field,name="poll_add_field"),
    path('poll_new/<poll_id>/', views.poll_new,name="poll_new"),

    path('verificar_campo/', views.verificar_campo, name='verificar_campo'),

    path('territorial_list/', views.territorial_list,name="territorial_list"),
    path('territorial_list/<page>/', views.territorial_list,name="territorial_list"),
    path('poll_list_view/<poll_id>/', views.poll_list_view,name="poll_list_view"),
    path('recuperar_campos/', views.recuperar_campos, name='recuperar_campos'),
    path('guardar_informacion/', views.guardar_informacion, name='guardar_informacion'),

]  