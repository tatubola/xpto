#!/bin/bash

docker-compose -f ./docker-compose_dev.yml run django python manage.py dbshell < ./mysql_data/SQL/drop_database.sql

