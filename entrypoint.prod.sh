#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py makemigrations
python manage.py migrate
DJANGO_SUPERUSER_PASSWORD=$SQL_PASSWORD python manage.py createsuperuser --username=$SQL_USER --email=$SQL_EMAIL --noinput
python manage.py collectstatic --no-input
gunicorn keycard_shell.wsgi:application --bind 0.0.0.0:8000