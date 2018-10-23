<template>
  <div class="col-md-10">
    <h1>ASN {{asn}} - {{ix.nome_longo}}</h1>
    <h4>
      <a data-toggle="collapse" href="#collapsed-table-1" aria-expanded="false" aria-controls="collapsed-table-1" @click="showTable1 = !showTable1">
        <i class="fas" :class="showTable1 ? 'fa-chevron-circle-down' : 'fa-chevron-circle-right'"></i>
        Serviços Pagos
      </a>
    </h4>
    <div class="table-responsive collapse" id="collapsed-table-1">
      <table class="table table-hover">
        <thead>
          <th>PIX</th>
          <th>Tipo</th>
          <th>Preço</th>
          <th>Expiração</th>
        </thead>
        <tbody>
          <tr v-for="servico in servicosFaturados" :key="servico.uuid">
            <td class="align-middle">{{servico.pix}}</td>
            <td class="align-middle">{{servico.tipo}}</td>
            <td class="align-middle">R${{servico.preco}}</td>
            <td class="align-middle">{{servico.data_expiracao}}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <h4>
      <a data-toggle="collapse" href="#collapsed-table-2" aria-expanded="true" aria-controls="collapsed-table-2" @click="showTable2 = !showTable2">
        <i class="fas" :class="showTable2 ? 'fa-chevron-circle-down' : 'fa-chevron-circle-right'"></i>
        Serviços Abertos
      </a>
    </h4>
    <div class="table-responsive collapse show" id="collapsed-table-2">
      <table class="table table-hover">
        <thead>
<!--           <th>
            <input type="checkbox" v-model="checkAll" value="" />
          </th> -->
          <th>PIX</th>
          <th>Tipo</th>
          <th>Preço</th>
          <th>Expiração</th>
          <th>Meses Adiantados</th>
        </thead>
        <tbody>
          <tr v-for="servico in servicosAbertos" :key="servico.uuid">
<!--             <td class="align-middle">
              <input type="checkbox" v-model="servico.checked" value="">
            </td> -->
            <td class="align-middle">{{servico.pix}}</td>
            <td class="align-middle">{{servico.tipo}}</td>
            <td class="align-middle">R${{servico.preco}}</td>
            <td class="align-middle">{{servico.data_expiracao}}</td>
            <td class="align-middle">
              <input v-show="servico.recorrente" v-model="servico.meses" class=" form-control w-50" type="number" min="0" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <button type="button" class="btn btn-primary" data-toggle="modal" @click="openModal">
      Gerar fatura
    </button>
    <GerarFaturaModal :servicos="servicosSelecionados" :modal-id="modalId" @faturaGerada="reload"></GerarFaturaModal>
  </div>
</template>

<script>
import GerarFaturaModal from '@/modals/GerarFaturaModal.vue'
import Servico from '@/api/Servico'
import IX from '@/api/IX'

export default {
  name: 'services',
  components: {
    GerarFaturaModal
  },
  data () {
    return {
      modalId: 'gerarFaturaModal',
      showTable1: false,
      showTable2: true,
      asn: this.$route.params.asn,
      codigo: this.$route.params.ix,
      ix: {},
      servicosFaturados: [],
      servicosAbertos: []
    }
  },

  computed: {
    checkAll: {
      get () {
        return !this.servicosAbertos.some(servico => servico.checked === false)
      },
      set (isChecked) {
        this.servicosAbertos.forEach(function (servico) {
          servico.checked = isChecked
        })
      }
    },
    servicosSelecionados () {
      return this.servicosAbertos.filter(servico => servico.checked === true)
    }
  },

  methods: {
    async getServicosNaoFaturados () {
      const response = await Servico.getServicosNaoFaturadosPorIxAsn({ asn: this.asn, ix: this.codigo })
      for (var servico in response.data) {
        this.servicosAbertos.push({
          uuid: response.data[servico]['uuid'],
          tipo: response.data[servico]['tipo'],
          hash: response.data[servico]['hash'],
          preco: response.data[servico]['preco'],
          recorrente: response.data[servico]['recorrente'],
          data_expiracao: response.data[servico]['data_expiracao'],
          meses: 0,
          checked: true
        })
      }
    },
    async getServicosFaturados () {
      const response = await Servico.getServicosFaturadosPorIxAsn({ asn: this.asn, ix: this.codigo })
      for (var servico in response.data) {
        this.servicosFaturados.push({
          uuid: response.data[servico]['uuid'],
          tipo: response.data[servico]['tipo'],
          hash: response.data[servico]['hash'],
          preco: response.data[servico]['preco'],
          recorrente: response.data[servico]['recorrente'],
          data_expiracao: response.data[servico]['data_expiracao']
        })
      }
    },
    async getIX () {
      const response = await IX.getIX({ codigo: this.codigo })
      this.ix = response.data
      this.$store.commit('change_asn', this.asn)
      this.$store.commit('change_ix_codigo', this.ix.codigo)
    },
    reload () {
      console.log('Refaz chamadas de API')
      this.checkAll = false
    },
    openModal () {
      if (this.servicosSelecionados.length > 0) {
        $('#' + this.modalId).modal().show()
      } else {
        alert('Selecione pelo menos um serviço')
      }
    }
  },
  mounted () {
    this.getIX()
    this.getServicosFaturados()
    this.getServicosNaoFaturados()
  }
}
</script>
