from django.core import management

from ixbr_api.core.utils.makefake import *


class Command(management.BaseCommand):
    help = 'Create fake data in database for tests purpose'

    def handle(self, *args, **options):
        management.call_command("flush")
        # data = MakeFakeData()
        # data.makeData()
        management.call_command("createsantamaria")
        management.call_command("createsuperuser")
