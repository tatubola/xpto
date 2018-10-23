import Api from '@/api/Api'

export default {
  async postOrdemDeCompra (params) {
    let message = ''
    let data = ''
    await Api().post('/ordemdecompra/', params).then(response => {
      message = 'Ordem de Compra gerada'
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
