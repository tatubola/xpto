import Api from '@/api/Api'

export default {
  getParticipante (params) {
    return Api().get(`/participante/?asn=${params.asn}&ix_id__codigo=${params.ix}`)
  },
  async updateParticipante (params) {
    let message = ''
    await Api().patch(`/participante/${params.asn}/`, params.data).then(response => {
      message = 'Atualizado com sucesso'
    }).catch(error => {
      message = submitError(error.response.data)
    })
    return message
  }
}

function submitError (errors) {
  let message = []
  for (const errorField in errors) {
    message.push({ 'field': errorField, 'message': errors[errorField] })
  }
  return message
}
