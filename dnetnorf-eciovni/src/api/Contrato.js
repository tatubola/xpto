import Api from '@/api/Api'

export default {
  getContratoVigente (params) {
    return Api().get(`/contrato/?participante__asn=${params.asn}&ix__codigo=${params.ix}&assinado=${params.assinado}&vigente=true`)
  },
  async patchAssinaContrato (params) {
    return Api().patch(
      `/contrato/${params.contrato_uuid}/`,
      {assinado: true})
  }
}
