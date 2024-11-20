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

from management.models import Management
from registration.models import Profile
from department.models import Deparment
from incident.models import Incident
from core.utils import *
from poll.models import Request

@login_required
def management_list_active(request,page=None):    
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    profiles = Profile.objects.get(user_id = request.user.id)
    try:
        if page == None:
            page = request.GET.get('page')
        else:
            page = page
        if request.GET.get('page') == None:
            page = page
        else:
            page = request.GET.get('page')
        management_activate = Management.objects.filter(state='Activo').order_by('management_name')
        page = request.GET.get('page')
        paginator = Paginator(management_activate , QUANTITY_LIST)
        management_activate_list = paginator.get_page(page)
        template_name = 'management/management_list_active.html'    
        return render(request, template_name, {'management_activate_list':management_activate_list,'username': request.user.username,'flow':flow,'profiles':profiles,'page':page,'paginator':paginator})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')       
@login_required
def management_list_block(request,page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    profiles = Profile.objects.get(user_id = request.user.id)
    try:
        if page == None:
            page = request.GET.get('page')
        else:
            page = page
        if request.GET.get('page') == None:
            page = page
        else:
            page = request.GET.get('page')
        management_block = Management.objects.filter(state='Bloqueado').order_by('management_name')
        page = request.GET.get('page')
        paginator = Paginator(management_block , QUANTITY_LIST)
        management_block_list = paginator.get_page(page)
        template_name = 'management/management_list_block.html'    
        return render(request, template_name, {'management_block_list':management_block_list,'username': request.user.username,'flow':flow,'profiles':profiles,'page':page,'paginator':paginator})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')    
@login_required
def management_add(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if request.method == 'POST':
            management_name = request.POST.get('management_name')
            management_in_charge = request.POST.get('management_in_charge')
            management_in_charge_mail = request.POST.get('management_in_charge_mail')
            if management_name == '' or management_in_charge == '' or management_in_charge_mail == '':
                messages.warning(request, 'Debe ingresar toda la información')
                return redirect('management_list_active')   
            management_save = Management(
                user_id = request.user.id,
                management_name = management_name.title(),
                management_in_charge = management_in_charge.title(),                
                management_in_charge_mail = management_in_charge_mail.upper(),                
                )
            management_save.save()
            messages.success(request, 'Dirección agregada')
            return redirect('management_list_active')  
        else:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')       
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')       
@login_required
def management_block(request,management_id):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        management_count = Management.objects.filter(pk=management_id).count()
        if management_count == 0:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('department_activate_list')    
        department_count = Deparment.objects.filter(management_id=management_id).filter(state='Activo').count()
        if department_count > 0:
            messages.error(request, 'No es posible bloquear esta direción ya que tiene departamentos activos')
            return redirect('management_list_active') 
        poll_count = Incident.objects.filter(management_id=management_id).filter(state='Activo').count()
        if poll_count > 0:
            messages.error(request, 'No es posible bloquear esta dirección ya que tiene incidencias activas')
            return redirect('management_list_active')                        
        Management.objects.filter(pk=management_id).update(state='Bloqueado')
        messages.success(request, 'Dirección bloqueada')
        return redirect('management_list_active')
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')  
@login_required
def management_activate(request,management_id):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        management_count = Management.objects.filter(pk=management_id).count()
        if management_count == 0:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('department_activate_list')    
        Management.objects.filter(pk=management_id).update(state='Activo')
        messages.success(request, 'Dirección activada')
        return redirect('management_list_block')
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')  
@login_required
def management_edit(request,management_id): 
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        management_count = Management.objects.filter(pk=management_id).count()
        if management_count <= 0:
            messages.error(request, 'Hubo un error al editar una dirección')
            return redirect('check_group_main') 
        management_data = Management.objects.get(pk=management_id)
        management_user_data = User.objects.get(pk=management_data.user_id)
        template_name = 'management/management_edit.html'    
        return render(request,template_name,{'username': request.user.username,'management_data':management_data,'management_user_data':management_user_data})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')  
@login_required
def management_edit_save(request): 
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if request.method == 'POST':
            management_id = request.POST.get('management_id')
            management_name = request.POST.get('management_name')
            management_in_charge = request.POST.get('management_in_charge')
            management_in_charge_mail = request.POST.get('management_in_charge_mail')
            if management_name == '' or management_in_charge == '' or management_in_charge_mail == '' or management_id == '':
                messages.warning(request, 'Debe ingresar toda la información')
                return redirect('management_list_active')   
            management_data_count = Management.objects.filter(pk=management_id).count()
            if management_data_count <= 0:
                messages.error(request, 'Hubo un error, favor contactese con los administradores')
                return redirect('check_group_main')                  
            Management.objects.filter(pk=management_id).update(management_name = management_name.title())
            Management.objects.filter(pk=management_id).update(management_in_charge = management_in_charge.title())
            Management.objects.filter(pk=management_id).update(management_in_charge_mail = management_in_charge_mail.upper())
            messages.success(request, 'Dirección editada')
            return redirect('management_list_active')  
        else:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')       
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
    

#NUEVAS FUNCIONES!
    

#Funcion para Encuestas Enviadas
@login_required
def management_main(request,page=None):  
    session = int(check_profile_management(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    request_derived_list = Request.objects.filter(request_state='Derivada')
    template_name = 'management/management_main.html'  
    return render(request,template_name, {'request_derived_list': request_derived_list})

#Funcion para ver Encuestas Enviadas
@login_required
def management_view(request,page=None):    
    session = int(check_profile_management(request))
    if session == 4:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    template_name = 'management/management_view.html'  
    return render(request,template_name)

#Funcion para Encuestas en Progreso

@login_required
def management_in_progress(request,page=None):    
    session = int(check_profile_management(request))
    if session == 4:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    template_name = 'management/management_in_progress.html'  
    return render(request,template_name)

#Funcion para Encuestas Finalizadas
@login_required
def management_finish(request,page=None):    
    session = int(check_profile_management(request))
    if session == 4:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    template_name = 'management/management_finish.html'  
    return render(request,template_name)
    

#Funcion para Encuestas ver Perfil
@login_required
def management_view_profile(request):
    session = int(check_profile_management(request))
    if session == 4:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
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
    
    template_name = 'management/management_view_profile.html'
    return render(request, template_name, context )

@login_required
def accept_request(request, request_id):
    # Obtener la solicitud correspondiente o devolver un error 404 si no existe
    solicitud = get_object_or_404(Request, id=request_id)

    # Cambiar el estado de la solicitud
    solicitud.request_state = 'Aceptada'
    
    # Guardar la solicitud actualizada en la base de datos
    solicitud.save()
    messages.success(request, 'Solicitud Aceptada con exito')
    # Aquí puedes realizar las operaciones necesarias con el ID de la solicitud
    request_derived_list = Request.objects.filter(request_state='Derivada')
    return render(request, 'management/management_main.html', {'request_derived_list': request_derived_list}) 

@login_required
def reject_request(request, request_id):
    # Obtener la solicitud correspondiente o devolver un error 404 si no existe
    solicitud = get_object_or_404(Request, id=request_id)

    # Cambiar el estado de la solicitud
    solicitud.request_state = 'Rechazada'
    
    # Guardar la solicitud actualizada en la base de datos
    solicitud.save()
    messages.error(request, 'Solicitud Rechazada con exito')
    # Aquí puedes realizar las operaciones necesarias con el ID de la solicitud
    request_derived_list = Request.objects.filter(request_state='Derivada')
    return render(request, 'management/management_main.html', {'request_derived_list': request_derived_list}) 