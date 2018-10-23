<template>
  <div class="col-sm-8">
    <h1>ASN {{asn}} - {{ix.nome_longo}}</h1>
    <h2>Faturas Abertas</h2>
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <th></th>
          <th>Número</th>
          <th>Data</th>
          <th>Valor</th>
          <th>Pagar</th>
        </thead>
        <tbody>
          <tr v-for="fatura in faturasAbertas" :key="fatura.id_financeiro">
            <td><a :href="fatura.boleto_url"><i class="fas fa-info-circle"></i></a></td>
            <td v-html="maskIdFinanceiro(fatura.id_financeiro,'###.###.###')"></td>
            <td>{{fatura.vencimento}}</td>
            <td>R${{fatura.valor}}</td>
            <td>
              <div class="btn-group" role="group">
                <a :href="fatura.boleto_url" class="btn btn-primary">Boleto</a>
                <button class="btn btn-primary">PayPal</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <h2>Faturas Fechadas</h2>
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <th></th>
          <th>Número</th>
          <th>Data</th>
          <th>Valor</th>
          <th></th>
        </thead>
        <tbody>
          <tr v-for="fatura in faturasFechadas" :key="fatura.id_financeiro">
            <td><a :href="fatura.boleto_url"><i class="fas fa-info-circle"></i></a></td>
            <td v-html="maskIdFinanceiro(fatura.id_financeiro,'###.###.###')"></td>
            <td>{{fatura.vencimento}}</td>
            <td>R${{fatura.valor}}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
    <h2>Faturas Canceladas</h2>
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <th></th>
          <th>Número</th>
          <th>Data</th>
          <th>Valor</th>
          <th></th>
        </thead>
        <tbody>
          <tr v-for="fatura in faturasCanceladas" :key="fatura.id_financeiro">
            <td><a :href="fatura.boleto_url"><i class="fas fa-info-circle"></i></a></td>
            <td v-html="maskIdFinanceiro(fatura.id_financeiro,'###.###.###')"></td>
            <td>{{fatura.vencimento}}</td>
            <td>R${{fatura.valor}}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import Fatura from '@/api/Fatura'
export default {
  data () {
    return {
      asn: this.$route.params.asn,
      codigo: this.$route.params.ix,
      ix: {},
      faturas: []
    }
  },
  computed: {
    faturasAbertas () {
      return this.faturas.filter(fatura => fatura.estado === 'ABERTA')
    },
    faturasFechadas () {
      return this.faturas.filter(fatura => fatura.estado === 'FECHADA' || fatura.estado === 'PAGA')
    },
    faturasCanceladas () {
      return this.faturas.filter(fatura => fatura.estado === 'CANCELADA')
    }
  },
  methods: {
    async getFaturaPorParticipante () {
      const response = await Fatura.getFaturasPorParticipanteAsnIx({ asn: this.asn, ix: this.codigo })
      for (var fatura in response.data) {
        this.faturas.push({
          id_financeiro: response.data[fatura]['id_financeiro'],
          estado: response.data[fatura]['estado'],
          valor: response.data[fatura]['valor'],
          vencimento: response.data[fatura]['vencimento']
        })
      }
    },
    maskIdFinanceiro (valor, padraoMascara) {
      valor = valor.toString().padStart(9, '0')
      let numeroMascarado = 'IXBR01 '
      let k = 0
      for (var i = 0; i < padraoMascara.length; i++) {
        if (padraoMascara[i] === '#') {
          if (typeof valor[k] !== 'undefined') {
            numeroMascarado = numeroMascarado + valor[k++]
          }
        } else {
          if (typeof padraoMascara[i] !== 'undefined') {
            numeroMascarado = numeroMascarado + padraoMascara[i]
          }
        }
      }
      return numeroMascarado
    }
  },
  mounted () {
    this.getFaturaPorParticipante()
  }
}
</script>
<style scoped>
  .mb-1 {
    margin-bottom: 10px
  }

  .mt-2 {
    margin-top: 20px
  }

  .vcenter {
    display: inline-block;
    vertical-align: middle;
    float: none;
  }
  table tr td{
    padding-left: 0px
  }
</style>
