import environ

env = environ.Env()
env.read_env()


def get_ticket_api_url():
    return env('URL_TICKET_API')


def get_ticker_meuix_url():
    return env('URL_TICKET_MEUIX')
