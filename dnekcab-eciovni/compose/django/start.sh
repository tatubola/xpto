#!/bin/bash
M_LOOPS="10"
DB_PORT="3360"

if [ $DJANGO_SETTINGS_MODULE == 'config.settings.production' ]
 then
    DB_HOST="10.0.129.24"
 else
    DB_HOST="db"
fi

echo "$(date) - ${DB_HOST}:${DB_PORT} Reachable ! - Starting Daemon"
#start the daemon

python manage.py migrate --fake-initial
python manage.py runserver 0.0.0.0:9000
