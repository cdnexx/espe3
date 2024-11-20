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
from incident.models import Incident
from department.models import Deparment
from management.models import Management
from registration.models import Profile
from core.utils import *
from poll.models import Request

@login_required
def department_list_active(request,page=None):    
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    profiles = Profile.objects.get(user_id = request.user.id) 
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if page == None:
            page = request.GET.get('page')
        else:
            page = page
        if request.GET.get('page') == None:
            page = page
        else:
            page = request.GET.get('page')
        if flow == 1:
            management_list = Management.objects.filter(state='Activo').order_by('management_name')
        if flow == 2:
            management_list = []
        department_activate = Deparment.objects.filter(state='Activo').order_by('deparment_name')
        page = request.GET.get('page')
        paginator = Paginator(department_activate , QUANTITY_LIST)
        department_activate_list = paginator.get_page(page)
        template_name = 'department/department_list_active.html'    
        return render(request, template_name, {'department_activate_list':department_activate_list,'username': request.user.username,'flow':flow,'profiles':profiles,'management_list':management_list,page:'page','paginator':paginator})
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')  
@login_required
def department_list_deactive(request,page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    profiles = Profile.objects.get(user_id = request.user.id) 
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:  
        if page == None:
            page = request.GET.get('page')
        else:
            page = page
        if request.GET.get('page') == None:
            page = page
        else:
            page = request.GET.get('page')
        # Filtra las encuestas desactivadas y ordénalas por nombre
        department_deactivate = Deparment.objects.filter(state='Bloqueado').order_by('deparment_name')
        # Paginación
        paginator = Paginator(department_deactivate , QUANTITY_LIST)
        department_deactivate_list = paginator.get_page(page)
        template_name = 'department/department_list_deactive.html'    
        return render(request,template_name,{'username': request.user.username,'department_deactivate_list':department_deactivate_list,'flow':flow,'profiles':profiles,page:'page','paginator':paginator})
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main') 
@login_required
def department_add(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:   
        if request.method == 'POST':
            deparment_name = request.POST.get('deparment_name')
            deparment_in_charge = request.POST.get('deparment_in_charge')
            deparment_in_charge_mail = request.POST.get('deparment_in_charge_mail')
            if deparment_name == '' or deparment_in_charge == '' or deparment_in_charge_mail == '':
                messages.add_message(request, messages.INFO, 'Debe ingresar toda la información')
                return redirect('department_list_active')   
            management_id =request.POST.get('management_id')
            management_count = Management.objects.filter(pk=management_id).count()
            if management_count <= 0:
                messages.add_message(request, messages.INFO, 'Error en la dirección asociada')
                return redirect('department_list_active')   
            deparment_save = Deparment(
                user_id = request.user.id,
                management_id = management_id,
                deparment_name = deparment_name.title(),
                deparment_in_charge = deparment_in_charge.title(),                
                deparment_in_charge_mail = deparment_in_charge_mail.upper(), 
                )
            deparment_save.save()
            messages.add_message(request, messages.INFO, 'Departamento ingresado')
            return redirect('department_list_active')  
        else:
            messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')         
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')    
    

@login_required
def department_block(request,department_id):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:  
        #valido que la encuesta existe y se encuentre en estado creacion
        department_count = Deparment.objects.filter(pk=department_id).count()
        if department_count == 0:
            messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
            return redirect('department_activate_list')    
        department_data = Deparment.objects.get(pk=department_id)#data de la encuesta antes de que se edite el estado
        incident_count = Incident.objects.filter(deparment_id=department_id).filter(state='Activo').count()
        if incident_count > 0:
            messages.add_message(request, messages.INFO, 'No es posible bloquear este departamento ya que tiene incidencias activas')
            return redirect('department_list_active')           
        
        Deparment.objects.filter(pk=department_id).update(state='Bloqueado')
        messages.add_message(request, messages.INFO, 'Departamento desactivado')
        return redirect('department_list_active')
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')    
    
@login_required
def department_activate(request, department_id):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')

    try:  
        department = get_object_or_404(Deparment, pk=department_id, state='Bloqueado')
        department.state = 'Activo'
        department.save()

        messages.add_message(request, messages.INFO, 'Departamento activado')
        return redirect('department_list_deactive')
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')    
@login_required
def department_edit(request,department_id): 
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    profiles = Profile.objects.get(user_id = request.user.id) 
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:   
        management_list = Management.objects.filter(state='Activo').order_by('management_name')
        department_count = Deparment.objects.filter(pk=department_id).count()
        if department_count <= 0:
            messages.add_message(request, messages.INFO, 'Hubo un error al editar un departamento')
            return redirect('check_group_main')        
        department_data = Deparment.objects.get(pk=department_id)
        department_user_data = User.objects.get(pk=department_data.user_id)
        template_name = 'department/department_edit.html'    
        return render(request,template_name,{'username': request.user.username,'department_data':department_data,'department_user_data':department_user_data,'flow':flow,'profiles':profiles,'management_list':management_list})
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')    
@login_required
def department_edit_save(request): 
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    if flow == 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:   
        if request.method == 'POST':
            department_id = request.POST.get('department_id')
            deparment_name = request.POST.get('deparment_name')
            deparment_in_charge = request.POST.get('deparment_in_charge')
            deparment_in_charge_mail = request.POST.get('deparment_in_charge_mail')
            department_count = Deparment.objects.filter(pk=department_id).count()
            if department_count <= 0:
                messages.add_message(request, messages.INFO, 'Hubo un error al editar un departamento')
                return redirect('check_group_main') 
            if deparment_name == '' or deparment_in_charge == '' or deparment_in_charge_mail == '':
                messages.add_message(request, messages.INFO, 'Debe ingresar toda la información')
                return redirect('department_edit',department_id)   
            management_id =request.POST.get('management_id')
            management_count = Management.objects.filter(pk=management_id).count()
            if management_count <= 0:
                messages.add_message(request, messages.INFO, 'Error en la dirección asociada')
                return redirect('department_edit',department_id)  
            Deparment.objects.filter(pk=department_id).update(deparment_name = deparment_name.title()) 
            Deparment.objects.filter(pk=department_id).update(deparment_in_charge = deparment_in_charge.title()) 
            Deparment.objects.filter(pk=department_id).update(deparment_in_charge_mail = deparment_in_charge_mail.upper()) 
            Deparment.objects.filter(pk=department_id).update(management_id = management_id)    
            messages.add_message(request, messages.INFO, 'Departamento editado con éxito')
            return redirect('department_list_active',department_id) 
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main') 
    
#NUEVAS FUNCIONES!
    

#Funcion para Encuestas Enviadas
@login_required
def department_main(request,page=None):
    session = int(check_profile_department(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    request_open_list = Request.objects.filter(request_state='Abierta')
    template_name = 'department/department_main.html'  
    return render(request, template_name, {'request_open_list': request_open_list})

@login_required
def department_view(request,page=None):    
    session = int(check_profile_department(request))
    if session == 3:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    template_name = 'department/department_view.html'  
    return render(request,template_name)

@login_required
def department_in_progress(request,page=None):    
    session = int(check_profile_department(request))
    if session == 3:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    template_name = 'department/department_in_progress.html'  
    return render(request,template_name)

@login_required
def department_finish(request,page=None):    
    session = int(check_profile_department(request))
    if session == 3:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    template_name = 'department/department_finish.html'  
    return render(request,template_name)

#Funcion para Encuestas ver Perfil
@login_required
def department_view_profile(request):
    session = int(check_profile_department(request))
    if session == 3:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
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
    
    template_name = 'department/department_view_profile.html'
    return render(request, template_name, context )

#Funcion para manipular solicitudes
@login_required
def aceptar_solicitud(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        # Por ejemplo, puedes realizar alguna acción en base al ID y luego volver a renderizar la misma página
        request_open_list = Request.objects.filter(request_state='Abierta')
        return render(request, 'department/department_main.html', {'request_open_list': request_open_list})
    else:
        # Manejar el caso en el que no se haya realizado una solicitud POST
        return HttpResponse('No se realizó una solicitud POST')