# Hércules (IX API)

## Desenvolvendo

### Nomenclatura das branchs

ixapi_nome_anomesdia

---

## Rodando a aplicação

### Remove todas as imagens do docker

```
docker rm -f $(docker ps -a -q)
docker rmi -f $(docker images -a -q)
docker network rm $(docker network ls -q)
docker volume rm $(docker volume ls -q)
```

### Apaga os arquivos de migrations

```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
```

### Clona a branch master

```
git clone https://<usuario>@code.ceptro.br/scm/ix/ix-api.git
```

### Cria os dockers do projeto

```
cd ix-api/
docker-compose -f ./dev.yml build
```

### Criar os arquivos de migracao e criar a base

```
docker-compose -f ./dev.yml run django python manage.py makemigrations
docker-compose -f ./dev.yml run django python manage.py migrate
```

### Criar dados para teste do Sistema 

```
docker-compose -f ./dev.yml run django python manage.py createfakedata
```

(responder 'yes' para a pergunta sobre a deleção da base)

### Criar um usuário admin

```
docker-compose -f ./dev.yml run django python manage.py createsuperuser
```

(coloque algum usuário - email - e alguma senha)

### Subir o docker

```
docker-compose -f ./dev.yml up
docker-compose -f ./dev.yml run django python manage.py runserver
```

### Resetando banco de dados

```
docker-compose -f ./dev.yml run django python manage.py reset_db
```

### No seu navegador colocar

<http://127.0.0.1:8000/admin/>
Autentique-se com as credenciais cadastradas no comando de createsuperuser. Em Accounts, clique em Email addresses, depois clique no email que criou como superuser, marque Verified e salve.

### Para acessar o sistema, acesse a URL

<http://127.0.0.1:8000/core/>

---

## Rodando testes

### Rodando todos os testes

```
docker-compose -f ./dev.yml run django python manage.py test
```

### Teste de cobertura

```
docker-compose -f ./dev.yml run django coverage run manage.py test
docker-compose -f ./dev.yml run django coverage html
docker-compose -f ./dev.yml run django open htmlcov/index.html
```

### Rodando todos os testes com o pytest-django

```
docker-compose -f dev.yml run django py.test --reuse-db
```

### Teste de cobertura com o pytest-django

```
docker-compose -f ./dev.yml run django pytest --cov=ixbr_api --cov-report xml --reuse-db
```

#### Algumas opções do pytest-django

* **\-\-reuse-db**: reusa o banco de dados entre execuções dos testes (os dados são excluídos).
* **\-\-pdb**: inicia o pdb quando ocorrer erros.
* **\-n [INT]**: roda os testes paralelamente, onde [INT] é o número de threads desejado.
* **\-\-fail-on-template-vars**: falha caso haja variáveis inválidas nos templates.

Documentação do pytest: <http://pytest-django.readthedocs.io/en/latest/>

---

## Sobre as ferramentas

### Jenkins

Jenkins está configurado atualmente para Continuous Integration, é responsável em rodar todos os testes para cada branch do projeto, notificando o Bitbucket com o status.

Para verificar onde falhou é necessário acessar o Jenkins através da url <http://10.0.129.20:8080/job/ix-api/>, em **Build History** clique no número que corresponde à sua branch (isso é encontrado no Bitbucket, na tela de Branchs ou Pull Request, clicando no símbolo de falha na coluna Builds) e depois clique em **Console Output** e no final da tela terá os testes que falharam.

### Selenium

Para os testes, é utilizado o *web driver* do *Google Chrome*. Ele é obtido pelo contêiner *selenium*, que está contido em uma imagem do *docker*, portanto, não é necessário dar *build*.

Você pode verificar se ele está rodando acessando a URL `http://localhost:4444`.

Nos testes, são utilizado as portas de 8081 a 8100 para a comunicação do *django* com o *selenium/standalone-chrome*. Se for necessário aumentar a quantidade de portas, você alterar o arquivo `ix-api/compose/django/entrypoint.sh`, na linha onde se lê `THIS_DOCKER_CONTAINER_TEST_SERVER="$THIS_DOCKER_CONTAINER_IP:8081-8100"`.

---

### Isort

Isort é um utilitário / biblioteca Python para classificar as importações alfabeticamente e separadas automaticamente em seções. Ele fornece um utilitário de linha de comando, biblioteca Python e plugins para vários editores para classificar rapidamente todas as suas importações. Ele atualmente suporta de forma limpa Python 2.7 - 3.6 sem dependências.

Para rodar o isort em todo o projeto, basta: 

`isort --recursive .`

Ou para um determinado arquivo:

`isort <path/filename>`

### Sphinx

Sphinx é uma ferramenta que permite que desenvolvedores criem documentação em texto simples para geração fácil de saída em formatos que atendem a necessidades variadas.

Para rodar o sphinx:

`sphinx-build -b html <sourcedir> <builddir>`

### Sass
`sass ixbr_api/static/sass/project.scss ixbr_api/static/css/project.css`

## Backups

### Realizando backup do banco de dados

É necessário que o serviço esteja rodando `docker-compose -f ./dev.yml up`.

Para criar o backup, execute:

```docker-compose -f ./dev.yml run postgres backup```

Para listar os backups criados, execute:

```docker-compose -f ./dev.yml run postgres list-backups```

### Copiando diretório de backup para fora do docker

É necessário que o serviço esteja rodando `docker-compose -f ./dev.yml up` ou `docker-compose -f dev.yml run up postgres`.

Execute `docker ps` para listar os containers e copie o `<containerId>` do Postgres.

Para copiar a pasta de backups do container docker para sua máquina, use o comando preenchendo com `<containerId>` e o diretório que deseja salvar:

```docker cp <containerId>:/backups /host/path/target```

### Copiando arquivo de backup para dentro do docker

```docker cp filename.sql.gz <containerId>:/backups```

### Restaurando backup do banco de dados

Para restaurar o backup, é preciso que **apenas** o postgre esteja rodando `docker-compose -f dev.yml run up postgres`, então execute:

```docker-compose -f dev.yml run postgres restore filename.sql```
