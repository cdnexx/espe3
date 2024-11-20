FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/urban_

# Copia los archivos de dependencias al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto al contenedor
COPY . .

# Expone el puerto 8000 (necesario para Django por defecto)
EXPOSE 8000

# Comando por defecto para ejecutar el servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
