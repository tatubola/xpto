#!/bin/bash

docker-compose -f ./docker-compose_dev.yml up -d db

docker-compose -f ./docker-compose_dev.yml exec -T db mysql -e 'CREATE DATABASE invoice_api'
docker-compose -f ./docker-compose_dev.yml exec -T db mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'invoice_api'@'%'"
docker-compose -f ./docker-compose_dev.yml exec -T db mysql -e "FLUSH PRIVILEGES"

docker-compose -f ./docker-compose_dev.yml stop db
