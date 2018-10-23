import Api from '@/api/Api'

export default {
  getFaturasPorParticipanteAsnIx (params) {
    return Api().get('/fatura/?participante__asn=' + params.asn + '&participante__ix_id__codigo=' + params.ix)
  },
  async postFatura (params) {
    let message = ''
    let data = ''
    await Api().post('/fatura/', params.data).then(response => {
      message = 'Fatura gerada'
      data = response.data
    }).catch(error => {
      message = submitError(error.response.data)
    })
    return {
      'message': message,
      'data': data
    }
  }
}

function submitError (errors) {
  let message = []
  for (const errorField in errors) {
    message.push({ 'field': errorField, 'message': errors[errorField] })
  }
  return message
}
