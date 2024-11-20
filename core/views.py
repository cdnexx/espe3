from datetime import datetime, timedelta, date
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Avg, Q
from django.conf import settings 
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from administrator.models import Config
from registration.models import Profile
from incident.models import Incident
from poll.models import Poll, Fields, Request, RequestAnswer, RequestRecord

from core.utils import *
#metodos públicos
def home(request):
    return redirect('landing')
def landing_page (request):
    return render (request, 'core/landing.html')
def inicio(request):
    return render (request, 'core/inicio.html')
#fin metodos públicos
#metodos inicio session
@login_required
def pre_check_profile(request):
    #por ahora solo esta creada pero aún no la implementaremos
    pass
@login_required
def check_group_main(request): 
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()   
    except:
        messages.add_message(request, messages.INFO, 'Error al iniciar sessión')              
        return redirect('logout')
    if profile.group_id > 0 and profile.group_id < 6:
        if profile.group_id == 1 :
            return redirect('dashboard_admin')
        if profile.group_id == 2:
            return redirect('territorial_main')
        if profile.group_id == 3:
            return redirect('departamento_main')
        if profile.group_id == 4:
            return redirect('dirección_main')
        if profile.group_id == 5:
            return redirect('cuadrilla_main')
    else:
        return redirect('logout')
#fin metodos inicio session
#dashboard
@login_required
def dashboard_admin(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    profiles = Profile.objects.get(user_id = request.user.id)
    return render (request, 'core/dashboard_admin.html',{'flow':flow,'profiles':profiles})
@login_required
def territorial_main(request):
    return render (request, 'core/territorial_main.html')
@login_required
def departamento_main(request):
    session = int(check_profile_department(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    return render (request, 'core/dashboard_department.html')
@login_required
def dirección_main(request):
    session = int(check_profile_management(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    return render (request, 'core/dashboard_direccion.html')
#Solo para probrar
@login_required
def cuadrilla_main(request,page=None):  
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        profile = None
    if profiles.group_id != 5:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    if page == None:
        page = request.GET.get('page')
    else:
        page = page
    if request.GET.get('page') == None:
        page = page
    else:
        page = request.GET.get('page')    
    poll_activate = Poll.objects.filter(state='Activo').order_by('name')
    page = request.GET.get('page')
    paginator = Paginator(poll_activate, 10) 
    poll_activate_list = paginator.get_page(page)
    incident_list = Incident.objects.filter(state='Activo').values_list('name', flat=True).distinct()
    template_name = 'core/cuadrilla_main.html'    
    return render(request,template_name,{'profiles':profiles,'poll_activate_list':poll_activate_list,'incident_list':incident_list, 'username': request.user.username})

