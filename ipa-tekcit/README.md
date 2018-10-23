# Rodando a aplicação

### Remove todas as imagens do docker
```
docker rm -f $(docker ps -a -q)
docker rmi -f $(docker images -a -q)
docker network rm $(docker network ls -q)
docker volume rm $(docker volume ls -q)
```


### Cria os dockers do projeto
```
cd ix-api/
docker-compose build
```


### Subir o docker
```
docker-compose up
```
ou
```
docker-compose run flask python run.py
```


### Para acessar o sistema, acesse a URL:
http://127.0.0.1:8000/api/tickets


# Rodando testes

### Rodando todos os testes
```
docker-compose run django flask run_tests.py
```
