from django.contrib import admin

from .models import (IX, Contrato, Fatura, OrdemDeCompra, Participante,
                     PerfilParticipante, Servico)

# Register your models here.
admin.site.register(Contrato)
admin.site.register(Fatura)
admin.site.register(OrdemDeCompra)
admin.site.register(Participante)
admin.site.register(Servico)
admin.site.register(IX)
admin.site.register(PerfilParticipante)
