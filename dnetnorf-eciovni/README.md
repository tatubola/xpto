# IX Invoice Frontend

Frontend do projeto de cobrança de serviços do IX.br. O backend está no repositório [ix-invoice-backend](https://code.ceptro.br/projects/IX/repos/ix-invoice-backend).

Projeto em VueJS 2.0, com [VueX](https://vuex.vuejs.org/) e [Vue I18n](http://kazupon.github.io/vue-i18n) para tradução.

## Inicializando o projeto

```bash
# install dependencies and serve with hot reload at localhost:8081
docker-compose up --build
```

## Configurando para produção

```bash
# build for production with minification
docker-compose run node npm run build

# build for production and view the bundle analyzer report
docker-compose run node npm run build --report
```

## Executando testes

```bash
# run unit tests
docker-compose run node npm run test:unit
```

## Verificando seu código com lint

Vue possui instalado por padrão o ESLint, caso esteja com servidor inicializado, será rodado toda vez que um arquivo é salvo, exibindo os erros. Caso não esteja rodando o servidor, use o seguinte comando:

```bash
# run lint tests
docker-compose run node npm run lint:no-fix
```

Para aplicar automaticamente, utilize o comando:

```bash
# apply lint
docker-compose run node npm run lint
```
