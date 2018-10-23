<template>
  <div class="col-sm-12">
    <h1>Lista de IX</h1>
    <div class="table-responsive">
      <table class="table table-hover">
<!--         <thead>
          <tr>
            <th>
              Nome
            </th>
            <th>
              Opções
            </th>
          </tr>
        </thead> -->
        <tbody>
          <tr v-for="ix_object in ix" :key="ix_object.code">
            <a v-on:click="exibirOpcoes">
              <router-link
              :to="{name: 'services', params: { ix: ix_object.codigo, asn: asn}}">
                  {{ix_object.nome_longo}}
              </router-link>
            </a>
<!--             <td>
              ...
            </td> -->
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import IX from '@/api/IX'
export default {
  data () {
    return {
      ix: {},
      asn: this.$route.params.asn
    }
  },
  methods: {
    async getIXAPI () {
      const response = await IX.getIXPorParticipante({ asn: this.asn })
      this.ix = response.data
      this.$store.commit('change_asn', this.asn)
      this.$store.commit('change_ix_codigo', this.ix.codigo)
      this.$store.commit('displayOpcoes', true)
    },
    exibirOpcoes () {
      this.$store.commit('displayOpcoes', false)
    }
  },
  mounted () {
    this.getIXAPI()
  }
}
</script>
