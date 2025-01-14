#!/bin/sh

# Esperar a que PostgreSQL esté disponible
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Ejecutar migraciones de Django
python manage.py migrate

# Ejecutar el comando que se pase al contenedor (por ejemplo, `runserver`)
exec "$@"
