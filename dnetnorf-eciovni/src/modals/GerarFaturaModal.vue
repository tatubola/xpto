<template>
    <BaseModal :modal-id="modalId" @modalClosed="handleModalClosed">
      <template v-if="modalIndex==0">
        <template slot="modal-title">
          <h5 class="modal-title">Ordem de Compra</h5>
        </template>
        <template slot="modal-body">
          <fieldset>
            <div>
              <label for="ordemDeCompra">Código:</label>
              <input type="text" class="form-control" name="ordemDeCompra" v-model="ordemDeCompra" maxlength="30">
            </div>
          </fieldset>
        </template>
        <template slot="modal-footer">
          <button data-dismiss="modal" type="button" class="btn btn-secondary">Cancelar</button>
          <button @click="modalIndex=1" type="button" class="btn btn-primary">Próximo</button>
        </template>
      </template>

      <template v-if="modalIndex==1">
        <template slot="modal-title">
          <h5 class="modal-title">Resumo</h5>
        </template>
        <template slot="modal-body">
          <div class="table-responsive" id="collapsed-table-1">
            <table class="table table-hover">
              <thead>
                <th>Tipo</th>
                <th>Preço</th>
                <th>Expiração</th>
              </thead>
              <tbody>
                <tr v-for="servico in servicos" :key="servico.uuid">
                  <td class="align-middle">{{servico.tipo}}</td>
                  <td class="align-middle">R${{getPreco(servico)}}</td>
                  <td class="align-middle">
                    <span v-show="servico.recorrente">
                    {{addMonthToDate(servico.data_expiracao, servico.meses)}}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <b>Total</b>: R${{totalServicos}}
          </div>
        </template>
        <template slot="modal-footer">
          <button @click="modalIndex=0" class="btn btn-secondary">Voltar</button>
          <button @click="gerarFatura" type="button" class="btn btn-success">Finalizar</button>
        </template>
      </template>
    </BaseModal>
</template>

<script>
import Participante from '@/api/Participante'
import BaseModal from '@/modals/BaseModal.vue'
import Fatura from '@/api/Fatura'
import OrdemDeCompra from '@/api/OrdemDeCompra'

export default{
  props: [
    'modalId',
    'servicos'
  ],
  components: {
    BaseModal
  },
  data () {
    return {
      asn: this.$route.params.asn,
      ix: this.$route.params.ix,
      modalIndex: 0,
      ordemDeCompra: null,
      data: {
        'vencimento': 0,
        'valor': 0,
        'estado': 'Paga',
        'servicos': this.servicos,
        'participante': ''
      }
    }
  },
  computed: {
    totalServicos () {
      return this.servicos
        .map(this.getPreco)
        .reduce((ac, valor) => ac + valor)
    }
  },
  methods: {
    calculaVencimento () {
      this.data.vencimento = '2018-10-15' // TODo criar endpoint
    },
    async gerarFatura (e) {
      e.preventDefault()
      $('#' + this.modalId).modal('toggle')
      this.calculaVencimento()
      const data = this.data
      const response = await Fatura.postFatura({ data })
      if (response.message === 'Fatura gerada') {
        if (this.ordemDeCompra) {
          await OrdemDeCompra.postOrdemDeCompra({
            'fatura': response.data.uuid,
            'identificacao_oc': this.ordemDeCompra
          })
        }
        alert(response.message)
      } else {
        let errors = ''
        for (var errorMessage of response) {
          errors = errors + errorMessage['message']
        }
        alert(errors)
      }
      this.$emit('faturaGerada')
      location.reload()
    },
    handleModalClosed () {
      this.modalIndex = 0
    },
    addMonthToDate (date, monthToAdd) {
      let day = parseInt(date.split('-')[2])
      let month = parseInt(date.split('-')[1])
      let year = parseInt(date.split('-')[0])

      let newDate = new Date(year, month + parseInt(monthToAdd), day)
      return newDate.getDate() + '-' +
             this.pad(parseInt(newDate.getMonth()) + 1) + '-' +
             newDate.getFullYear()
    },
    pad (number) {
      return number.toString().padStart(2).replace(' ', 0)
    },
    getPreco (servico) {
      if (servico.recorrente) {
        return servico.preco * (parseInt(servico.meses) + 1)
      } else {
        return servico.preco
      }
    },
    async getParticipanteAPI () {
      const response = await Participante.getParticipante({ asn: this.asn, ix: this.ix })
      this.data.participante = response.data[0].uuid
    }
  },
  mounted () {
    this.getParticipanteAPI()
  }
}
</script>
