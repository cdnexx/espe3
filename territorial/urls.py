from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from territorial import views

territorial_patterns = [
    path('territorial_main/', views.territorial_main,name="territorial_main"),
    path('territorial_list/', views.territorial_list,name="territorial_list"),
    path('territorial_list/<page>/', views.territorial_list,name="territorial_list"),
    path('territorial_poll_view/<poll_id>/', views.territorial_poll_view,name="territorial_poll_view"),
    path('territorial_request_poll/<poll_id>/', views.territorial_request_poll,name="territorial_request_poll"),
    path('territorial_request_save/', views.territorial_request_save,name="territorial_request_save"),
    #revisar
    path('territorial_list_inprogress/', views.territorial_list_inprogress,name="territorial_list_inprogress"),
    path('territorial_list_inprogress/<page>/', views.territorial_list_inprogress,name="territorial_list_inprogress"),

    path('territorial_list_finished/', views.territorial_list_finished,name="territorial_list_finished"),
    path('territorial_list_finished/<page>/', views.territorial_list_finished,name="territorial_list_finished"),

    path('territorial_poll_view_process/<poll_id>/', views.territorial_poll_view_process,name="territorial_poll_view_process"),

    path('territorial_poll_view_finished/<poll_id>/', views.territorial_poll_view_finished,name="territorial_poll_view_finished"),

    path('territorial_poll_start/<poll_id>/', views.territorial_poll_start,name="territorial_poll_start"),

    path('ver_perfil/', views.ver_perfil, name='ver_perfil'),

    path('poll_list_sent/', views.poll_list_sent,name="poll_list_sent"),
]

