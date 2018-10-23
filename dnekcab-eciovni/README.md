# Introdução

Este repositório contém o código fonte do projeto INVOICE, que consiste no sistema de pagamento do meu-ix. A implementação é feita com Docker e o framework Django.

É importante observar que este repositório contempla apenas o backend do projeto. O frontend está localizando no repositório IX/repos/ix-invoice-frontend.

# Instalação

1. Clone o repositório
```console
user@bar:$  git clone <url_repositorio>
```


2. Depois de clonado, faça o `build` dos containers
```console
user@bar:$  docker-compose -f ./docker-compose_dev.yml build
```


3. Execute o script de criação do banco
```console
user@bar:$  ./create_db.sh
```


4. Aplique os arquivos de migração
```console
user@bar:$  docker-compose -f ./docker-compose_dev.yml run django python manage.py migrate
```

5. Suba o docker
```console
user@bar:$  docker-compose -f ./docker-compose_dev.yml up
```

Abra no seu navegador a url http://localhost:9000/api/v1/ para visualizar os endpoints definidos.

# Populando Base de Dados

Neste projeto é necessário manter a base de dados com os participantes e IX's já existentes. Para isso, foram criados alguns scripts que conectam na base de dados do meu-ix atual. Para proceder com a população da base, siga os passos abaixo:

1. Instale as libs para poder executar o script.
```console
user@bar:$  cd migracao/
user@bar:$  pip install -r requirements.txt
```


2. Gere o arquivo que será usado para popular o banco.
```console
user@bar:$  cd migracao/
user@bar:$  python3.6 import_data.py
user@bar:$  cp -p ./output/importa_participante_<timestamp> ../
user@bar:$  cp -p ./output/importa_ix_<timestamp> ../
```

Obs.: O arquivo terá um timestamp (epoch) que muda todas as vezes que o script é executado.


3. Através do `shell_plus` importe os dados para a base de dados do Django.
```console
user@bar:$  docker-compose -f ./docker-compose_dev.yml run django python manage.py shell_plus
<output concatenado>

>>> file_to_compile = open('./importa_participante_<timestamp>').read()
>>> code_obj = compile(file_to_compile, '', 'exec')
>>> exec(code_obj)
>>> quit()
```

O mesmo processo deve ser feito com o arquivo `importa_ix_<timestamp>`.

# Troubleshooting

## Reinstalação dos Containers e do Banco de Dados

Principalmente durante o inicio do desenvolvimento do sistema, é comum a alteração de modelos e, com isso, a necessidade de recirar ou reaplicar os arquivos de migração.

1. Destrua todos os containers do projeto
```console
user@bar:$  docker-compose -f ./docker-compose_dev.yml down
```


2. Destrua a base de dados
```console
user@bar:$  ./drop_db.sh
```


3. Remova os arquivos de migração (se for o caso e **tenha certeza de que está no diretorio raiz do projeto correto**)
```console
user@bar:$  find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
user@bar:$  find . -path "*/migrations/*.pyc"  -delete
```


4. Siga os passos de 2 e 3 da [Instalação](#Instalação)


5. Recrie os arquivos de migração
```console
user@bar:$  docker-compose -f ./docker-compose_dev.yml run django python manage.py makemigrations
```


6. Siga os passo 4 e 5 da [Instalação](#Instalação)

## Erro de Conexão com o Banco de Dados

1. Verifique se a porta 3306 não está sendo utiliza por nenhum outro container
```console
user@bar:$  docker ps
```

Observe a coluna `PORTS`. A porta 3306 não deveria estar aparendo em outros containers, senão aquele do projeto.


2. Caso tenha algum container utilizando a porta, destrua-o com o comando abaixo:
```console
user@bar:$  docker rm -f <docker UUID>
```


3. Em alguns casos, pode haver outro processo escutando na porta 3306 (ex. alguma instancia do MySQL que subiu na sua máquina no processo de boot). Para verificar se esse é o caso:
```console
root@bar:#  netstat -anp | grep 3306
```

Caso tenha algum processo utilizando esta porta, verifique a possibilidade de matar o processo.
