import Api from '@/api/Api'

export default {
  getServicoPorIxParticipanteUuid (params) {
    return Api().get('/servico/?participante=' + params.participante + '&ix=' + params.ix)
  },
  getServicosNaoFaturadosPorIxAsn (params) {
    return Api().get('/servicos-nao-faturados/' + params.asn + '/' + params.ix + '/')
  },
  getServicosFaturadosPorIxAsn (params) {
    return Api().get('/servicos-faturados/' + params.asn + '/' + params.ix + '/')
  }
}
