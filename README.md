# Pasos para levantar la aplicación

1.	Cree un entorno virtual y ejecute el siguiente comando pip install -r requirements.txt
2.	Cree una base de datos desde la consola de postgreeSQL
3.	Colóquese en la raíz del sistema y ejecute el siguiente comando cp settings.txt urban/ settings.py
4.	Configure el archivo settings.py de acuerdo con los parámetros entregados por el administrador del sistema.
5.	Ejecute el siguiente comando python manage.py mekemigrations
6.	Ejecute el siguiente comando python manage.py migrate
7.	Ejecute la consola de su base de datos, una vez en ella active la base de datos agregada para la        aplicación, una vez seleccionada la base de datos ejecute las siguientes consultas SQL.

    INSERT INTO auth_group VALUES(1,'Admin');
    INSERT INTO auth_group VALUES(2,'Territorial');    
    INSERT INTO auth_group VALUES(3,'Departamento');  
    INSERT INTO auth_group VALUES(4,'Dirección');      
    INSERT INTO auth_group VALUES(5,'Cuadrilla');  
    INSERT INTO administrator_config VALUES(1,'nombre municipalidad',1,'2024-01-01','2024-01-01');
    INSERT INTO registration_profile VALUES(0,'default','default',1,1);
    INSERT INTO management_management VALUES(0,'default','default','default','default','2024-01-01','2024-01-01',1);    
    INSERT INTO department_deparment VALUES(0,'default','default','2024-01-01','2024-01-01',1,0,'default','default');    
    INSERT INTO incident_incident VALUES(0,'default','default','2024-01-01','2024-01-01',1,0,0);    
# Tipos de flujo 
    1 => Flujo Depatamentos
    2 => Flujo Direcciones
# Grupos de usuario
    1 => Admin
    2 => Territorial
    3 => Departamento
    4 => Dirección
    5 => Cuadrilla

# Para crear un vista use la siguiente plantilla para el backend
@login_required
def nombreapp_functionname(request):
    session = int(check_profile_admin(request))
    if session == 0:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('logout')
    flow = type_flow(request)
    template_name = 'nombreapp/nombreapp_functionname.html'    
    return render(request, template_name, {'profiles': profiles,'username': request.user.username,'flow':flow})
