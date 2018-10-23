from django.core import management

from ixbr_api.core.utils.make_santamariadata import *


class Command(management.BaseCommand):
    help = 'Create data related to Santa Maria PIX (RIA)'

    def handle(self, *args, **options):
        # management.call_command("flush")
        ria = MakeSantaMaria()
        print("Creating PIX for Santa Maria")
        ria.createRIAPix()

        print("Creating IX for Joao Pessoa")
        ria.createJPA()        
        ria.createJPApix()

        print("Creating Switches for Santa Maria")
        ria.createRIASwitche_01()
        ria.createRIASwitche_02()

        print("Creating ASN for Santa Maria AND Joao Pessoa")
        ria.createRIAASN()
        ria.createRIAContacts()

        print("Allocation IPs for Santa Maria")
        ria.createIPsRIA()

        ria.createChannelPortRIA()
        ria.createPortRIA()
        ria.createCustomerChannelRIA()
        ria.createCoreChannelRIA()
        ria.tagsRIA()
        ria.servicesRIA()

        # data.makeData()
        # management.call_command("create_santamaria")

        print("Creating Switches for Joao Pessoa")
        ria.createJPASwitche_01()
        ria.createJPASwitche_02()
        ria.createJPASwitche_03()


        print("Allocation IPs for Joao Pessoa")
        ria.createIPsJPA()
        print("Creating ChannelPort for Joao Pessoa")
        ria.createChannelPortJPA()
        print("Creating Ports for Joao Pessoa")
        ria.createPortJPA()
        print("Creating CustomerChannel for Joao Pessoa")
        ria.createCustomerChannelJPA()
        print("Creating InfraChannel for Joao Pessoa")
        ria.createInfraChannelJPA()
        print("Creating Tags for Joao Pessoa")
        ria.tagsJPA()
        print("Creating Services for Joao Pessoa")
        ria.servicesJPA()
