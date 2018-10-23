import Api from '@/api/Api'

export default {
  getIX (params) {
    return Api().get(`ix/${params.codigo}/`)
  },
  getIXPorParticipante (params) {
    return Api().get(`ix-por-participante/${params.asn}/`)
  }
}
