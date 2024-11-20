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
from django.http import JsonResponse

from incident.models import Incident
from poll.models import Poll, Fields
from registration.models import Profile
from core.utils import *
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@login_required
def poll_main(request,page=None):  
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
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
    paginator = Paginator(poll_activate, 20) 
    poll_activate_list = paginator.get_page(page)

    poll_deactivate = Poll.objects.filter(state='Bloqueado').order_by('name')
    page = request.GET.get('page')
    paginator = Paginator(poll_deactivate, 20) 
    poll_deactivate_list = paginator.get_page(page)
    template_name = 'poll/poll_main.html'    
    return render(request,template_name,{'poll_activate_list':poll_activate_list,'poll_deactivate_list':poll_deactivate_list, 'username': request.user.username,'flow':flow})
@login_required
def poll_list_deactivate(request, page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    if page is None:
        page = request.GET.get('page')
    # Filtra las encuestas desactivadas y ordénalas por nombre
    poll_deactivate = Poll.objects.filter(state='Bloqueado').order_by('name')
    # Paginación
    paginator = Paginator(poll_deactivate, 20)
    poll_deactivate_list = paginator.get_page(page)
    template_name = 'poll/poll_list_deactivate.html'    
    return render(request, template_name, {'flow':flow,'poll_deactivate_list': poll_deactivate_list, 'page': page, 'username': request.user.username})

@login_required
def poll_list_create(request, page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    if page is None:
        page = request.GET.get('page')
    # Filtra las encuestas en creación y ordénalas por nombre
    poll_create = Poll.objects.filter(state='creacion').order_by('name')
    # Paginación
    paginator = Paginator(poll_create, 20)
    poll_create_list = paginator.get_page(page)
    template_name = 'poll/poll_list_create.html'    
    return render(request, template_name, {'flow': flow, 'poll_create_list': poll_create_list, 'page': page, 'username': request.user.username})

@login_required
def poll_view(request,poll_id):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)  
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('poll_main')    
    #obtengo la encuesta creada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other').order_by('name')
    template_name = 'poll/poll_view.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username,'flow':flow}) 

@login_required
def poll_edit(request, poll_id):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)  
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('poll_main')
    incidents = Incident.objects.filter(state='Activo').order_by('name')
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other').order_by('name')
    poll_fields_block = Fields.objects.filter(poll_id=poll_id).filter(state='bloqueado').order_by('name')
    campos_bloqueados = Fields.objects.filter(poll_id=poll_id, state='bloqueado')
    template_name = 'poll/poll_edit.html'
    return render(request, template_name, {'campos_bloqueados' : campos_bloqueados, 'incidents': incidents, 'poll_data': poll_data,'poll_fields_standard_array': poll_fields_standard_array,'poll_fields_other':poll_fields_other,'poll_fields_block':poll_fields_block, 'username': request.user.username,'flow':flow})


#revisar
@require_GET
def verificar_campo(request):
    campo = request.GET.get('campo', None)
    if campo:
        # Verificar si el campo ya existe en la base de datos
        exists = Fields.objects.filter(name=campo).exists()
        if exists:
            message = f'El campo "{campo}" ya existe.'
        else:
            message = f'El campo "{campo}" está disponible.'
        return JsonResponse({'exists': exists, 'message': message})
    else:
        return JsonResponse({'exists': False, 'message': 'Campo no proporcionado'})
    
def add_field(user_id,poll_id,name,label,placeholder,kind):
    try:
        field_save = Fields(
            user_id = user_id,
            poll_id = poll_id,
            name = name,
            label = label,
            placeholder = placeholder,
            kind = kind,
            )
        field_save.save()
        return 0
    except:
        return 1

def count_space(string):
    count = 0
    for i in range(0, len(string)):
        if string[i] == " ":
            count += 1         
    return count

@login_required
def poll_add(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')   
    #creamos la encuesta en estado creacion con los atributos por defecto, el nombre en este punto será generico
    poll_save = Poll(
        user_id = request.user.id,
        incident_id = 0, #usamos el tipo por defecto
        name = 'Encuesta en proceso',
        state = 'creacion',
        )
    poll_save.save()
    poll_id = poll_save.id 
    #fin encuesta por defecto
    #creamos los campos por defecto
    error = 0
    if add_field(request.user.id,poll_id,'name_neighbor','Nombre Vecino','Nombre Vecino','Defecto') == 1:
        error = 1
    if add_field(request.user.id,poll_id,'mail_neighbor','Correo Vecino','Correo Vecino','Defecto') == 1:
        error = 1
    if add_field(request.user.id,poll_id,'pohne_neighbor','Teléfono Vecino','Teléfono Vecino','Defecto') == 1:                                          
        error = 1
    if add_field(request.user.id,poll_id,'rut_neighbor','RUT','RUT','Defecto') == 1:                                          
        error = 1
    if add_field(request.user.id,poll_id,'incidence_priority','Prioridad','Prioridad','Defecto') == 1:
        error = 1
    if add_field(request.user.id,poll_id,'incidence_description','Descripcion','Descripcion','Defecto') == 1:
        error = 1
    if add_field(request.user.id,poll_id,'incidence_latitud','Latitud','Latitud','Defecto') == 1:
        error = 1
    if add_field(request.user.id,poll_id,'incidence_longitud','Longitud','Longitud','Defecto') == 1:
        error = 1 
    if add_field(request.user.id,poll_id,'incidence_image','Imagen','Imagen','Defecto') == 1:
        error = 1 
    if add_field(request.user.id,poll_id,'incidence_video','Video','Video','Defecto') == 1:
        error = 1 
    if add_field(request.user.id,poll_id,'incidence_audio','Audio','Audio','Defecto') == 1:
        error = 1 
    if error == 1:
        messages.add_message(request, messages.INFO, 'Uno de los campos no se guardó')
    #creamos los campos por defecto
    return redirect('poll_edit',poll_id)




def recuperar_campos(request):
    if request.method == 'POST':
        campos_seleccionados = request.POST.getlist('campos[]')
        
        # Lógica para cambiar el estado de los campos seleccionados a 'Activo'
        for campo_nombre in campos_seleccionados:
            campos = Fields.objects.filter(name=campo_nombre)
            for campo in campos:
                campo.state = 'Activo'
                campo.save()

        return JsonResponse({'message': 'Campos recuperados con éxito'})
    else:
        return JsonResponse({'message': 'Solicitud no válida'}, status=400)


#listados

#funciones
@login_required
def poll_block(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')    
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('poll_main')    
    pool_data = Poll.objects.get(pk=poll_id)#data de la encuesta antes de que se edite el estado
    Poll.objects.filter(pk=poll_id).update(state='Bloqueado')
    messages.add_message(request, messages.INFO, 'Encuesta bloqueada')
    return redirect('poll_main')

@login_required
def poll_activate(request, poll_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')
    try:
        Poll.objects.get(pk=poll_id, state='Bloqueado')
    except Poll.DoesNotExist:
        messages.add_message(request, messages.INFO, 'La encuesta no existe o no está bloqueada')
        return redirect('poll_main')
    Poll.objects.filter(pk=poll_id).update(state='Activo')
    messages.add_message(request, messages.INFO, 'Encuesta activada')
    # time.sleep(1)
    return redirect('poll_list_deactivate')


@login_required
def poll_add_end(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')  
    if request.method == 'POST':
        poll_id = request.POST.get('poll_id')
        poll_name = request.POST.get('poll_name')
        incident = request.POST.get('incident')
        if poll_name == '' or incident == '' or poll_id == '':
            messages.add_message(request, messages.INFO, 'Error al guardar encuesta')
            return redirect('poll_main')       
        #valido que la encuesta existe y se encuentre en estado creacion
        pool_count = Poll.objects.filter(pk=poll_id).count()
        if pool_count == 0:
            messages.add_message(request, messages.INFO, 'Error al guardar encuesta')
            return redirect('poll_main')
        incident_count = Incident.objects.filter(pk=incident).count()
        if incident_count <= 0:
            messages.add_message(request, messages.INFO, 'Error al guardar encuesta')
            return redirect('poll_main')
        Poll.objects.filter(pk=poll_id).update(name=poll_name)
        Poll.objects.filter(pk=poll_id).update(incident_id=incident)
        Poll.objects.filter(pk=poll_id).update(state='Activo')
        messages.add_message(request, messages.INFO, 'Encuesta activada')
        return redirect('poll_main')

@login_required
def poll_edit_end(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')  
    if request.method == 'POST':
        poll_id = request.POST.get('poll_id')
        poll_name = request.POST.get('poll_name')
        incident = request.POST.get('incident')
        if poll_name == '' or incident == '' or poll_id == '':
            messages.add_message(request, messages.INFO, 'Error al guardar encuesta')
            return redirect('poll_main')       
        #valido que la encuesta existe y se encuentre en estado creacion
        pool_count = Poll.objects.filter(pk=poll_id).count()
        if pool_count == 0:
            messages.add_message(request, messages.INFO, 'Error al guardar encuesta')
            return redirect('poll_main')
        incident_count = Incident.objects.filter(pk=incident).count()
        if incident_count <= 0:
            messages.add_message(request, messages.INFO, 'Error al guardar encuesta')
            return redirect('poll_main')
        Poll.objects.filter(pk=poll_id).update(name=poll_name)
        Poll.objects.filter(pk=poll_id).update(incident_id=incident)
        Poll.objects.filter(pk=poll_id).update(state='Activo')
        messages.add_message(request, messages.INFO, 'Encuesta activada')
        return redirect('poll_main')

@login_required
def guardar_informacion(request):
    if request.method == 'POST':
        poll_id = request.POST.get('poll_id')
        poll_name = request.POST.get('poll_name')
        incident = request.POST.get('incident')
        if poll_name == '' or incident == '' or poll_id == '':
            return JsonResponse({'success': False, 'message': 'Error al guardar encuesta'})

        # Valida que la encuesta existe y se encuentra en estado creación
        poll = get_object_or_404(Poll, pk=poll_id)
        incident_count = Incident.objects.filter(pk=incident).count()

        if incident_count <= 0:
            return JsonResponse({'success': False, 'message': 'Error al guardar encuesta'})

        poll.name = poll_name
        poll.incident_id = incident
        poll.state = 'creacion'
        poll.save()

        return JsonResponse({'success': True, 'message': 'Encuesta activada'})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
@login_required
def poll_add_field(request, poll_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al agregar un nuevo campo')
        return redirect('poll_main')
    if request.method == 'POST':
        nuevo_campo_nombre = request.POST.get('nuevo_campo_nombre')
        nuevo_campo_label = request.POST.get('nuevo_campo_label')
        if nuevo_campo_nombre == '' or nuevo_campo_label == '':
            messages.add_message(request, messages.INFO, 'Los campos no pueden estar vacios')
            return redirect('poll_edit',poll_id)
        
        name_count = Fields.objects.filter(poll_id=poll_id).filter(name=nuevo_campo_nombre).count()
        if name_count > 0:
            messages.add_message(request, messages.INFO, 'El nombre de campo ya existe '+str(nuevo_campo_nombre))
            return redirect('poll_edit',poll_id)            
        #agregar validacion sin espacios
        string_spaces = count_space(nuevo_campo_nombre)
        if string_spaces > 0:
            messages.add_message(request, messages.INFO, 'El campo nombre '+str(nuevo_campo_nombre)+' no debe contener espacios')
            return redirect('poll_edit',poll_id)       
        nuevo_campo = Fields(
            user=request.user,
            poll_id=poll_id,
            name=nuevo_campo_nombre,
            label=nuevo_campo_label,
            placeholder=nuevo_campo_label,
            kind_field = 'other',
            kind="Defecto",
            state="Activo"
        )
        nuevo_campo.save()
        messages.add_message(request, messages.INFO, 'Campo agregado')
        return redirect('poll_edit',poll_id)
    else:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear un nuevo campo')
        return redirect('check_group_main')

@login_required
def poll_fields_delete(request,poll_id,field):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')  
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al eliminar un campo')
        return redirect('poll_main')    
    field_data = Fields.objects.filter(poll_id=poll_id).filter(name=field).first()
    Fields.objects.filter(pk=field_data.id).update(state='bloqueado') 
    return redirect('poll_edit',poll_id)

#evaluar borrar

from django.shortcuts import render



@login_required
def poll_new(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')    
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('poll_main')    
    #obtengo los tipos de incidencia
    incidents =  Incident.objects.filter(state='Activo').order_by('name')
    #obtengo la encuesta creada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other')

    template_name = 'poll/poll_new.html'    
    return render(request,template_name,{'incidents':incidents,'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other}) 

##PRUEBA ACA 
@login_required
def territorial_list(request,page=None):  
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        # Manejar el caso donde el perfil no se encuentra
        profile = None
    if profiles.group_id != 1:
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
    poll_sent = Poll.objects.filter(state='Enviado').order_by('name')
    page = request.GET.get('page')
    paginator = Paginator(poll_sent, 20) 
    poll_list_sent = paginator.get_page(page)
    #print("asdkjas",poll_sent)

    template_name = 'poll/territorial_list.html'    
    return render(request,template_name,{'profiles':profiles,'poll_list_sent':poll_list_sent, 'username': request.user.username})

@login_required
def poll_list_view(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')    
    #valido que la encuesta existe y se encuentre en estado enviado
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al crear la nueva encuesta')
        return redirect('poll_main')    
    #obtengo la encuesta enviada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Enviado').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)
    
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Enviado').filter(kind_field='other').order_by('name')
    
    template_name = 'poll/poll_list_view.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username}) 