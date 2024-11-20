from django.shortcuts import render
from registration.models import Profile
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, time
from poll.models import Poll, Fields, Request, RequestAnswer, RequestRecord
from department.models import Deparment
from incident.models import Incident
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.files.storage import FileSystemStorage

@login_required
def territorial_main(request):  
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'territorial/territorial_main.html'  
    return render(request,template_name,{'profiles':profiles})
@login_required
def territorial_list(request,page=None):  
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        profile = None
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    page = request.GET.get('page') if page is None else page if request.GET.get('page') is None else request.GET.get('page')  
    
    #poll_activate = Poll.objects.filter(Q(state='Rechazado') | Q(state='creacion')).order_by('name')
    poll_activate = Poll.objects.filter(state='Activo').order_by('name')
    page = request.GET.get('page')
    paginator = Paginator(poll_activate, 20) 
    poll_activate_list = paginator.get_page(page)
    incident_list = Incident.objects.filter(Q(state='Rechazado') | Q(state='creacion')).values_list('name', flat=True).distinct()
    template_name = 'territorial/territorial_list.html'  
    return render(request,template_name,{'profiles':profiles,'poll_activate_list':poll_activate_list,'incident_list':incident_list, 'username': request.user.username})
@login_required
def territorial_poll_view(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')    
    #valido que la encuesta existe y se encuentre en estado creacion
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error al acceder a la encuesta')
        return redirect('territorial_main')    
    #obtengo la encuesta creada
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)    
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other').order_by('name')
    template_name = 'territorial/territorial_poll_view.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username}) 
@login_required
def territorial_request_poll(request, poll_id):
    #Validaciones de usuario
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error, la encuesta no se encutra. Contactar al Administrador')
        return redirect('territorial_main')
    
    #Obtencion de campos para la encuesta
    incidents = Incident.objects.filter(state='Activo').order_by('name')
    poll_data = Poll.objects.get(pk=poll_id)
    poll_fields_standard_array = []
    poll_fields_standard = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='standard')
    for p in poll_fields_standard:
        poll_fields_standard_array.append(p.name)
    poll_fields_other = Fields.objects.filter(poll_id=poll_id).filter(state='Activo').filter(kind_field='other').order_by('name')
    template_name = 'territorial/territorial_request_poll.html'
    
    return render(request, template_name, {'incidents': incidents, 'poll_data': poll_data,'poll_fields_standard_array': poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username})

@login_required
def territorial_request_save(request):
    #Validaciones de usuario
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    
    #Obtencion de ID para asociar la request
    if request.method == 'POST':
            poll_id = request.POST.get('poll_id')
    poll_data = Poll.objects.get(pk=poll_id)

    #Validar Encuesta
    pool_count = Poll.objects.filter(pk=poll_id).count()
    if pool_count == 0:
        messages.add_message(request, messages.INFO, 'Hubo un error, la encuesta no se encuentra. Contactar al Administrador')
        return redirect('territorial_main')

    #Crear la request
    request_save=Request(
        user_id= request.user.id,
        poll_id = poll_id,
        deparment_id = poll_data.incident.deparment.id,
        request_name ='Rquest1',
        request_date ='2024-03-29',
    )
    request_save.save()

    #Rellenar la encuesta con los datos ingresados por el territorial
    fields_data = Fields.objects.filter(poll_id=poll_data.id).filter(state='Activo').order_by('id')
    images = request.FILES.getlist('incidence_image')
    fs= FileSystemStorage()
    for r in fields_data:
        if r.name=='incidence_image':
            for i in images:
                file_path=fs.save(i.name,i)
                uploaded_file_path=fs.url(file_path)
                request_answ_save=RequestAnswer(
                    request_answer_text= request.POST.get(r.name),
                    fields_id=r.id,
                    request_id=request_save.id,
                    user_id=request.user.id,
                )
                request_answ_save.save()
        
        else:
            request_answ_save=RequestAnswer(
            request_answer_text= request.POST.get(r.name),
            fields_id=r.id,
            request_id=request_save.id,
            user_id=request.user.id,
            )
        request_answ_save.save()
    messages.add_message(request, messages.INFO, 'Encuesta creada')
    return redirect('territorial_list')  



#revisar
@login_required
def poll_list_sent(request, page=None):
    profiles = Profile.objects.get(user_id=request.user.id)
    
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una área para la que no tiene permisos')
        return redirect('check_group_main')

    if page is None:
        page = request.GET.get('page')

    # Filtra las encuestas desactivadas y ordénalas por nombre
    poll_deactivate = Poll.objects.filter(state='Enviado').order_by('name')

    # Paginación
    paginator = Paginator(poll_deactivate, 20)
    poll_list_sent = paginator.get_page(page)

    template_name = 'territorial/poll_list_sent.html'    
    return render(request, template_name, {'profiles': profiles, 'poll_list_sent': poll_list_sent, 'page': page, 'username': request.user.username})


#Revisar ya que es codigo para procesar y visualizar templates
@login_required
def territorial_list_inprogress(request,page=None):  
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        profile = None
    if profiles.group_id != 2:
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
    poll_activate = Poll.objects.filter(Q(state='Activo') | Q(state='Proceso')).order_by('name')
    page = request.GET.get('page')
    paginator = Paginator(poll_activate, 20) 
    poll_activate_list = paginator.get_page(page)
    incident_list = Incident.objects.filter(Q(state='Activo') | Q(state='Proceso')).values_list('name', flat=True).distinct()
    template_name = 'territorial/territorial_list_inprogress.html'    
    return render(request,template_name,{'profiles':profiles,'poll_activate_list':poll_activate_list,'incident_list':incident_list, 'username': request.user.username})
    

@login_required
def territorial_list_finished(request,page=None):  
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        profile = None
    if profiles.group_id != 2:
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
    poll_activate = Poll.objects.filter(Q(state='Finalizado') | Q(state='Bloqueado')).order_by('name')
    page = request.GET.get('page')
    paginator = Paginator(poll_activate, 20) 
    poll_activate_list = paginator.get_page(page)
    incident_list = Incident.objects.filter(Q(state='Finalizado') | Q(state='Bloqueado')).values_list('name', flat=True).distinct()
    template_name = 'territorial/territorial_list_finished.html'    
    return render(request,template_name,{'profiles':profiles,'poll_activate_list':poll_activate_list,'incident_list':incident_list, 'username': request.user.username})
 
@login_required
def territorial_poll_view_process(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 2:
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
    template_name = 'territorial/territorial_poll_view_process.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username}) 

@login_required
def territorial_poll_view_finished(request,poll_id):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 2:
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
    template_name = 'territorial/territorial_poll_view_finished.html'    
    return render(request,template_name,{'poll_data':poll_data,'poll_fields_standard_array':poll_fields_standard_array,'poll_fields_other':poll_fields_other, 'username': request.user.username}) 




@login_required
def territorial_poll_start(request, poll_id):
    profiles = Profile.objects.get(user_id=request.user.id)
    if profiles.group_id != 2:
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
    template_name = 'territorial/territorial_poll_start.html'
    
    return render(request, template_name, {
        'poll_data': poll_data,
        'poll_fields_standard_array': poll_fields_standard_array,
        'poll_fields_other': poll_fields_other,
        'username': request.user.username,
        'current_poll_id': poll_id,  # Añade la ID de la encuesta al contexto
    })
@login_required
def ver_perfil(request):
    try:
        profiles = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    if profiles.group_id != 2:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    user = request.user
    user = request.user

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
    template_name = 'territorial/ver_perfil.html'
    return render(request, template_name, context)
