import os

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
from manuals.models import Manuals
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from administrator.models import Config, Logo
from registration.models import Profile
from administrator.forms import upload_logo_form, UploadLogoForm
from os import remove
from core.utils import *

@login_required
def administrator_main(request):  
    session = int(check_profile_admin(request))
    if session == 0:
        messages.error(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        config_data = Config.objects.get(pk=1)
        logo_data = Logo.objects.filter(state='Activa').first()
        profiles = Profile.objects.get(user_id = request.user.id)
        flow = type_flow(request)
        template_name = 'administrator/administrator_main.html'  
        manuals_list = Manuals.objects.all()
        page = request.GET.get('page')
        paginator = Paginator(manuals_list , QUANTITY_LIST)
        manuals_list_pag = paginator.get_page(page)  
        return render(request,template_name,{'profiles':profiles,'config_data':config_data,'logo_data':logo_data,'flow':flow , 'manuals_list_pag':manuals_list_pag,'paginator':paginator})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')       
@login_required
def administrator_logo_edit(request):  
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        config_data = Config.objects.get(pk=1)
        logo_data = Logo.objects.filter(state='Activa').first()
        logo_form = upload_logo_form(1)
        profiles = Profile.objects.get(user_id = request.user.id)
        flow = type_flow(request)
        template_name = 'administrator/administrator_logo_edit.html'    
        return render(request,template_name,{'profiles':profiles,'config_data':config_data,'logo_data':logo_data,'logo_form':logo_form,'flow':flow})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required
def administrator_logo_save(request):  
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')    
    #pasamos todas la imagenes antiguas a desactivas
    Logo.objects.filter(state='Activa').update(state='Desactiva')
    form = UploadLogoForm(request.POST, request.FILES)
    if form.is_valid():  
        name_file = request.FILES['path']
        form.save()
        path_delete = os.path.join(settings.BASE_DIR,'registration','static','registration','img')
        delete_file = path_delete+'\logo_mun.png'
        name_file_base = 'logo_mun.png'
        try:
            remove(delete_file)
        except:
            delete_file = path_delete+'\logo_mun.png'
        try:
            path_up = os.path.join(settings.BASE_DIR,'core','static','core','admin','logo',str(name_file))
            path_new = os.path.join(settings.BASE_DIR,'registration','static','registration','img',str(name_file_base))
            os.rename(path_up, path_new)
        except:
            messages.error(request, 'Error al editar el logo')
            return redirect('administrator_main')
    messages.success(request, 'Logo editado con éxito')
    return redirect('administrator_main')
#gestión de usuario
@login_required
def administrator_users_main(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        # Obtener la lista de grupos
        groups = Group.objects.exclude(pk=0).order_by('id')
        for group in groups:
            group.active_user_count = User.objects.filter(profile__group=group, is_active=True).count()
            group.inactive_user_count = User.objects.filter(profile__group=group, is_active=False).count()
        template_name = 'administrator/administrator_users_main.html'
        return render(request,template_name,{'groups':groups,'username': request.user.username,'flow':flow})
    except Exception as e:
        messages.error(request, f'Hubo un error: {e}')
        return redirect('check_group_main')   
@login_required
def administrator_users_main_active(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        groups = Group.objects.all().exclude(pk=0).order_by('id')
        template_name = 'administrator/administrator_users_main_active.html'
        return render(request,template_name,{'groups':groups,'username': request.user.username,'flow':flow})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required
def administrator_users_main_block(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        groups = Group.objects.all().exclude(pk=0).order_by('id')
        template_name = 'administrator/administrator_users_main_block.html'
        return render(request,template_name,{'groups':groups,'username': request.user.username,'flow':flow})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required
def administrator_users_new(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        groups = Group.objects.all().exclude(pk=0).order_by('id')
        template_name = 'administrator/administrator_users_new.html'
        return render(request,template_name,{'groups':groups,'username': request.user.username,'flow':flow})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')               
@login_required
def administrator_users_save(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if request.method == 'POST':
            profile = request.POST.get('profile')       
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            if profile == '' or first_name == '' or last_name == '' or email == '':
                messages.warning(request, 'Debe ingresar toda la información')
                return redirect('administrator_users_main')  
            profile_count = Group.objects.filter(pk=profile).count()
            if profile_count <= 0:
                messages.error(request, 'Hubo un error, favor contactese con los administradores')
                return redirect('check_group_main')              
            mail_exist = User.objects.filter(email=email).count()
            if mail_exist == 0:
                user = User.objects.create_user(
                    username= email,
                    email=email,
                    password=email,
                    first_name=first_name,
                    last_name=last_name,
                    )
                profile_save = Profile(
                    user_id = user.id,
                    group_id = profile,
                    )
                profile_save.save()
                messages.success(request, 'Usuario creado con éxito')    
                return redirect('administrator_users_main')                         
            else:
                messages.warning(request, 'El correo que esta tratando de ingresar, ya existe en nuestros registros')                             
                return redirect('administrator_users_main')   
        else:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')               
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')           
@login_required
def administrator_users_edit(request, user_id, page = None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        user_data_count = User.objects.filter(pk=user_id).count()
        if user_data_count <= 0:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')          
        groups = Group.objects.all().exclude(pk=0).order_by('id')
        user_data = User.objects.get(pk=user_id)
        profile_data_user_edit = Profile.objects.get(user_id=user_id)
        template_name = 'administrator/administrator_users_edit.html'
        return render(request,template_name,{'groups':groups,'user_data':user_data,'username': request.user.username,'flow':flow,'profile_data_user_edit':profile_data_user_edit,'page':page})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required
def administrator_edit_save(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if request.method == 'POST':       
            page = request.POST.get('page')               
            user_data_id = request.POST.get('user_data')               
            profile = request.POST.get('profile')       
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            if page == '':
                page = 1
            if user_data_id == '':
                messages.error(request, 'Hubo un error, favor contactese con los administradores')
                return redirect('check_group_main')              
            user_data_count = User.objects.filter(pk=user_data_id).count()
            if user_data_count <= 0:
                messages.error(request, 'Hubo un error, favor contactese con los administradores')
                return redirect('check_group_main')          
            if profile == '' or first_name == '' or last_name == '' or email == '':
                messages.warning(request, 'Debe ingresar toda la información')
                return redirect('administrator_users_new')  
            profile_count = Group.objects.filter(pk=profile).count()
            if profile_count <= 0:
                messages.error(request, 'Hubo un error, favor contactese con los administradores')
                return redirect('check_group_main')              
            user_data_after = User.objects.get(pk=user_data_id)
            if user_data_after.email != email:
                mail_exist = User.objects.filter(email=email).exclude(pk=user_data_id).count()
                if mail_exist > 0:
                    messages.warning(request, 'El correo que esta tratando de ingresar, ya existe en nuestros registros')                             
                    return redirect('administrator_users_edit',user_data_id)                       
            User.objects.filter(pk=user_data_id).update(first_name=first_name)   
            User.objects.filter(pk=user_data_id).update(last_name=last_name)                    
            User.objects.filter(pk=user_data_id).update(email=email)            
            Profile.objects.filter(user_id=user_data_id).update(group_id=profile)            
            messages.success(request, 'Usuario editado con éxito')    
            return redirect('administrator_users_list_active', profile) 
        else:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')           
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required    
def administrator_users_list_active(request,profie_id,page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        profile_count = Group.objects.filter(pk=profie_id).count()
        if profile_count <= 0:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')      
        if page == None:
            page = request.GET.get('page')
        else:
            page = page
        if request.GET.get('page') == None:
            page = page
        else:
            page = request.GET.get('page')
        group = Group.objects.get(pk=profie_id)
        user_all = []
        user_array = User.objects.filter(is_active='t').filter(profile__group_id=profie_id).order_by('first_name')
        for us in user_array:
            name = us.first_name+' '+us.last_name   
            user_all.append({'id':us.id,'user_name':us.username,'name':name,'mail':us.email,'first_name':us.first_name,'last_name':us.last_name})
        paginator = Paginator(user_all, QUANTITY_LIST)  
        user_list = paginator.get_page(page)
        template_name = 'administrator/administrator_users_list_active.html'
        return render(request,template_name,{'username': request.user.username,'group':group,'user_list':user_list,'paginator':paginator,'page':page,'flow':flow})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required    
def administrator_users_list_block(request,profie_id,page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    try:
        profile_count = Group.objects.filter(pk=profie_id).count()
        if profile_count <= 0:
            messages.error(request, 'Hubo un error, favor contactese con los administradores')
            return redirect('check_group_main')      
        if page == None:
            page = request.GET.get('page')
        else:
            page = page
        if request.GET.get('page') == None:
            page = page
        else:
            page = request.GET.get('page')
        group = Group.objects.get(pk=profie_id)
        user_all = []
        user_array = User.objects.filter(is_active='f').filter(profile__group_id=profie_id).order_by('first_name')
        for us in user_array:
            name = us.first_name+' '+us.last_name   
            user_all.append({'id':us.id,'user_name':us.username,'name':name,'mail':us.email})
        paginator = Paginator(user_all, QUANTITY_LIST)  
        user_list = paginator.get_page(page)
        template_name = 'administrator/administrator_users_list_block.html'
        return render(request,template_name,{'username': request.user.username,'group':group,'user_list':user_list,'paginator':paginator,'page':page,'flow':flow})
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')   
@login_required
def administrator_users_block(request, user_id, page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if page == None:
            page = 1
        user_data_count = User.objects.filter(pk=user_id).count()
        profile_data = Profile.objects.get(user_id=user_id)       
        if user_data_count > 0:
            user_data = User.objects.get(pk=user_id)
            User.objects.filter(pk=user_id).update(is_active='f')
            messages.success(request, 'Usuario '+user_data.first_name +' '+user_data.last_name+' bloqueado con éxito')
            return redirect('administrator_users_list_active',profile_data.group_id)        
        else:
            messages.error(request, 'Hubo un error ')
            return redirect('administrator_users_list_active',profile_data.group_id,page)        
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')           
@login_required
def administrator_users_activate(request, user_id, page=None):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    try:
        if page == None:
            page = 1
        user_data_count = User.objects.filter(pk=user_id).count()
        profile_data = Profile.objects.get(user_id=user_id)       
        if user_data_count > 0:
            user_data = User.objects.get(pk=user_id)
            User.objects.filter(pk=user_id).update(is_active='t')
            messages.success(request, 'Usuario '+user_data.first_name +' '+user_data.last_name+' activado con éxito')
            return redirect('administrator_users_list_block',profile_data.group_id,page)        
        else:
            messages.error(request, 'Hubo un error ')
            return redirect('administrator_users_list_block',profile_data.group_id,page)     
    except:
        messages.error(request, 'Hubo un error, favor contactese con los administradores')
        return redirect('check_group_main')           
    

@login_required
def administrator_view_profile_main(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.warning(request, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    user = request.user
    profiles = Profile.objects.get(user_id = request.user.id)
    flow = type_flow(request)

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
        'flow':flow,
        
    }
    
    template_name = 'administrator/administrator_view_profile_main.html'
    return render(request, template_name, context )

@login_required
def manual_upload_direccion(request):
    if request.method == 'POST' and request.FILES['myfiledireccion']:
        myfile = request.FILES['myfiledireccion']
        extension = myfile.name.split('.')[-1].lower()
        if extension == 'pdf':
            # Guarda el archivo en el sistema de archivos
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url_direccion = fs.url(filename)
            
            # Obtiene el nombre del manual y la descripción del formulario
            manual_name = "Manual Dirección"
            manual_description = "Proporciona instrucciones detalladas de manejo de este módulo."
            
            # Guarda la información del manual en la base de datos
            manual = Manuals(
                manual_name=manual_name.title(),
                manual_path=uploaded_file_url_direccion,
                manual_description=manual_description.title()
            )
            manual.save()
            manuals_list = Manuals.objects.all()
            page = request.GET.get('page')
            paginator = Paginator(manuals_list , QUANTITY_LIST)
            manuals_list_pag = paginator.get_page(page)
            # Muestra un mensaje de éxito
            messages.success(request, 'Manual ingresado')
            return render(request,'administrator/administrator_main.html',{
                'uploaded_file_url_direccion': uploaded_file_url_direccion, 'manuals_list_pag':manuals_list_pag,'paginator':paginator
            })

        else:
            # Muestra un mensaje de error si el archivo no es PDF
            messages.warning(request, 'Solo se permiten archivos PDF')
    return redirect('administrator_main')

@login_required
def manual_upload_departamento(request):
    if request.method == 'POST' and request.FILES['myfiledepartamento']:
        myfile = request.FILES['myfiledepartamento']
        extension = myfile.name.split('.')[-1].lower()
        if extension == 'pdf':
            # Guarda el archivo en el sistema de archivos
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url_departamento = fs.url(filename)
            
            # Obtiene el nombre del manual y la descripción del formulario
            manual_name = "Manual Departamento"
            manual_description = "Proporciona instrucciones detalladas de manejo de este módulo."
            
            # Guarda la información del manual en la base de datos
            manual = Manuals(
                manual_name=manual_name.title(),
                manual_path=uploaded_file_url_departamento,
                manual_description=manual_description.title()
            )
            manual.save()
            manuals_list = Manuals.objects.all()
            page = request.GET.get('page')
            paginator = Paginator(manuals_list , QUANTITY_LIST)
            manuals_list_pag = paginator.get_page(page)
            # Muestra un mensaje de éxito
            messages.success(request, 'Manual ingresado')
            return render(request,'administrator/administrator_main.html',{
                'uploaded_file_url_departamento': uploaded_file_url_departamento, 'manuals_list_pag':manuals_list_pag,'paginator':paginator
            })

        else:
            # Muestra un mensaje de error si el archivo no es PDF
            messages.warning(request, 'Solo se permiten archivos PDF')
    return redirect('administrator_main')

@login_required
def manual_upload_incidente(request):
    if request.method == 'POST' and request.FILES['myfileincidente']:
        myfile = request.FILES['myfileincidente']
        extension = myfile.name.split('.')[-1].lower()
        if extension == 'pdf':
            # Guarda el archivo en el sistema de archivos
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url_incidente = fs.url(filename)
            
            # Obtiene el nombre del manual y la descripción del formulario
            manual_name = "Manual Incidente"
            manual_description = "Proporciona instrucciones detalladas de manejo de este módulo."
            
            # Guarda la información del manual en la base de datos
            manual = Manuals(
                manual_name=manual_name.title(),
                manual_path=uploaded_file_url_incidente ,
                manual_description=manual_description.title()
            )
            manual.save()
            manuals_list = Manuals.objects.all()
            page = request.GET.get('page')
            paginator = Paginator(manuals_list , QUANTITY_LIST)
            manuals_list_pag = paginator.get_page(page)
            # Muestra un mensaje de éxito
            messages.success(request, 'Manual ingresado')
            return render(request,'administrator/administrator_main.html',{
                'uploaded_file_url_incidente': uploaded_file_url_incidente , 'manuals_list_pag':manuals_list_pag,'paginator':paginator
            })

        else:
            # Muestra un mensaje de error si el archivo no es PDF
            messages.warning(request, 'Solo se permiten archivos PDF')
    return redirect('administrator_main')

@login_required
def manual_upload_encuesta(request):
    if request.method == 'POST' and request.FILES['myfileencuesta']:
        myfile = request.FILES['myfileencuesta']
        extension = myfile.name.split('.')[-1].lower()
        if extension == 'pdf':
            # Guarda el archivo en el sistema de archivos
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url_encuesta = fs.url(filename)
            
            # Obtiene el nombre del manual y la descripción del formulario
            manual_name = "Manual Encuesta"
            manual_description = "Proporciona instrucciones detalladas de manejo de este módulo."
            
            # Guarda la información del manual en la base de datos
            manual = Manuals(
                manual_name=manual_name.title(),
                manual_path=uploaded_file_url_encuesta,
                manual_description=manual_description.title()
            )
            manual.save()
            manuals_list = Manuals.objects.all()
            page = request.GET.get('page')
            paginator = Paginator(manuals_list , QUANTITY_LIST)
            manuals_list_pag = paginator.get_page(page)
            # Muestra un mensaje de éxito
            messages.success(request, 'Manual ingresado')
            return render(request,'administrator/administrator_main.html',{
                'uploaded_file_url_encuesta': uploaded_file_url_encuesta, 'manuals_list_pag':manuals_list_pag,'paginator':paginator
            })

        else:
            # Muestra un mensaje de error si el archivo no es PDF
            messages.warning(request, 'Solo se permiten archivos PDF')
    return redirect('administrator_main')

@login_required
def manual_upload_configuracion(request):
    if request.method == 'POST' and request.FILES['myfileconfiguracion']:
        myfile = request.FILES['myfileconfiguracion']
        extension = myfile.name.split('.')[-1].lower()
        if extension == 'pdf':
            # Guarda el archivo en el sistema de archivos
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url_configuracion = fs.url(filename)
            
            # Obtiene el nombre del manual y la descripción del formulario
            manual_name = "Manual Configuración"
            manual_description = "Proporciona instrucciones detalladas de manejo de este módulo."
            
            # Guarda la información del manual en la base de datos
            manual = Manuals(
                manual_name=manual_name.title(),
                manual_path=uploaded_file_url_configuracion,
                manual_description=manual_description.title()
            )
            manual.save()
            manuals_list = Manuals.objects.all()
            page = request.GET.get('page')
            paginator = Paginator(manuals_list , QUANTITY_LIST)
            manuals_list_pag = paginator.get_page(page)
            # Muestra un mensaje de éxito
            messages.success(request, 'Manual ingresado')
            return render(request,'administrator/administrator_main.html',{
                'uploaded_file_url_configuracion': uploaded_file_url_configuracion, 'manuals_list_pag':manuals_list_pag,'paginator':paginator
            })

        else:
            # Muestra un mensaje de error si el archivo no es PDF
            messages.warning(request, 'Solo se permiten archivos PDF')
    return redirect('administrator_main')