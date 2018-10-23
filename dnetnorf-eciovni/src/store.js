import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    asn: 0,
    ix: 'ix',
    exibirOpcoes: false
  },
  mutations: {
    change_asn (state, newAsn) {
      state.asn = newAsn
    },
    change_ix_codigo (state, newIx) {
      state.ix = newIx
    },
    displayOpcoes (state, opcao) {
      state.exibirOpcoes = opcao
    }
  },
  actions: {

  }
})
