from django.core import management
from invoice_api.core.utils.makefake import *


class Command(management.BaseCommand):
    help = "Cria dados falsos para testes no FrontEnd"

    def handle(self, *args, **options):

        management.call_command("flush")
        fake = Makefakedata()
        fake.createServicosEmFaturaCancelada()
        fake.createServicosEmFaturaPaga()
        fake.createServicoComExpiracaoFutura()
