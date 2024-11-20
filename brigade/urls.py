from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from brigade import views

brigade_patterns = [
    #path('incident_add/', views.incident_add,name="incident_add"),
        #Probando templates
    path('brigade_list_progress',views.brigade_list_progress,name='brigade_list_progress'), 
    path('brigade_list_finish',views.brigade_list_finish,name='brigade_list_finish'), 

    path('brigade_poll_view_progress/<poll_id>/',views.brigade_poll_view_progress,name='brigade_poll_view_progress'), 
    path('brigade_poll_view_finish/<poll_id>/',views.brigade_poll_view_finish,name='brigade_poll_view_finish'), 
    path('brigade_poll_start/<poll_id>/',views.brigade_poll_start,name='brigade_poll_start'), 
    path('brigade_view_profile',views.brigade_view_profile,name='brigade_view_profile'), 
    
]