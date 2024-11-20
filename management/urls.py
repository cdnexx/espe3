from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from management import views

management_patterns = [
    path('management_list_active', views.management_list_active,name="management_list_active"),
    path('management_list_active/<page>/', views.management_list_active,name="management_list_active"),
    path('management_list_block', views.management_list_block,name="management_list_block"),
    path('management_list_block/<page>/', views.management_list_block,name="management_list_block"),
    path('management_add', views.management_add,name="management_add"),
    path('management_block/<management_id>/', views.management_block,name="management_block"),
    path('management_activate/<management_id>/', views.management_activate,name="management_activate"),
    path('management_edit/<management_id>/', views.management_edit,name="management_edit"),
    path('management_edit_save/', views.management_edit_save,name="management_edit_save"),

    #NUEVOS
    path('management_main/', views.management_main,name="management_main"),
    path('management_view/<request_id>/', views.management_view,name="management_view"),    
    path('management_in_progress/', views.management_in_progress,name="management_in_progress"),
    path('management_finish/', views.management_finish,name="management_finish"),
    path('management_view_profile/', views.management_view_profile,name="management_view_profile"),
    path('accept_request/<request_id>/', views.accept_request,name="accept_request"), 
    path('reject_request/<request_id>/', views.reject_request,name="reject_request"),
     
]   