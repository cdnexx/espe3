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

#Probando los templates

@login_required
def brigade_list_progress(request,page=None):  
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
    template_name = 'brigade/brigade_list_progress.html'    
    return render(request,template_name,{'profiles':profiles,'poll_activate_list':poll_activate_list,'incident_list':incident_list, 'username': request.user.username})
@login_required
def brigade_list_finish(request,page=None):  
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
    template_name = 'brigade/brigade_list_finish.html'    
    return render(request,template_name,{'profiles':profiles,'poll_activate_list':poll_activate_list,'incident_list':incident_list, 'username': request.user.username})


@login_required
def brigade_poll_view_progress(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 5:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')    
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('territorial_main')    
    #obtengo la encuesta creada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)    
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other').order_by('name')
    template_name = 'brigade/brigade_poll_view_progress.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username}) 

@login_required
def brigade_poll_view_finish(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 5:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')    
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('territorial_main')    
    #obtengo la encuesta creada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)    
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other').order_by('name')
    template_name = 'brigade/brigade_poll_view_finish.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username}) 




@login_required
def brigade_poll_start(request, poll_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 5:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')

    # Valida que la encuesta existe y se encuentre en estado de creación
    poll_count = Poll.objects.filter(pk=poll_id).count()
    if poll_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('territorial_main')

    # Obtiene la encuesta creada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id, state='Activo', kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)

    poll_fields_other = Fields.objects.filter(poll_id=poll_id, state='Activo', kind_field='other').order_by('name')
    template_name = 'brigade/brigade_poll_start.html'
    
    return render(request, template_name, {
        'poll_data': poll_data,
        'poll_fields_standard_array': poll_fields_standard_array,
        'poll_fields_other': poll_fields_other,
        'username': request.user.username,
        'current_poll_id': poll_id,  # Añade la ID de la encuesta al contexto
    })
@login_required
def brigade_view_profile(request):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 5:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a un área para la que no tiene permisos')
        return redirect('check_group_main')
    user = request.user
    profiles = Profile.objects.get(user_id = request.user.id)

    if request.method == 'POST':
        # Si se envía un formulario de edición, actualiza los datos
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente.')

    # Obtiene los datos actualizados del usuario
    user.refresh_from_db()

    context = {
        'user_data': user,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'cargo': profiles.group.name, 
    }
    
    template_name = 'brigade/brigade_view_profile.html'
    return render(request, template_name, context )
