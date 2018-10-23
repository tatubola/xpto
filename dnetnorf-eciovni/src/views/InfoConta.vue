<template>
    <div class="info_conta">
      <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item">
            <a href="#conta" class="nav-link active"  id="conta-tab" role="tab" aria-controls="conta" aria-selected="true" data-toggle="tab">Conta</a>
          </li>
          <li role="presentation">
            <a href="#contrato" class="nav-link" id="contrato-tab" role="tab" aria-controls="contrato" aria-selected="false" data-toggle="tab">Contrato</a>
          </li>
      </ul>
        <div class="tab-content">
            &nbsp;
            <!-- BEGIN: Formulario de contato -->
            <div role="tabpanel" class="tab-pane fade show active" id="conta"  aria-labelledby="conta-tab">
                <div class="col-md-8">
                  <h4 class="page-header">DADOS CADASTRAIS</h4>
                  <form role="form" @submit.prevent="updateParticipante">
                    <div class="row">
                        <div class="col-md-6 form-group float-label-control">
                            <label for="">ASN</label>
                            <input data-vv-as="ASN" v-validate="'max_value:4199999999'" type="number" class="form-control" name="asn" v-model="form.asn" required disabled>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('asn')">{{ errors.first('asn') }}</p>
                            </transition>
                        </div>

                        <div class="col-md-6 form-group float-label-control">
                            <label for="">CNPJ</label>
                            <input v-mask="'##.###.###/####-##'" data-vv-as="CNPJ" type="text" class="form-control" name="cnpj" v-model="form.cnpj" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('cnpj')">{{ errors.first('cnpj') }}</p>
                            </transition>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-12 form-group float-label-control">
                            <label for="">Razão social</label>
                            <input data-vv-as="Razao Social" type="text" class="form-control" name="razao_social" v-model="form.razao_social" required>
                        </div>
                        <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                            <p class="alert" v-if="errors.has('razao_social')">{{ errors.first('razao_social') }}</p>
                        </transition>
                    </div>

                    <div class="row">
                        <div class="col-md-12 form-group float-label-control">
                            <label for="">Responsável</label>
                            <input data-vv-as="Responsavel" type="text" class="form-control" name="responsavel" v-model="form.responsavel" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('responsavel')">{{ errors.first('responsavel') }}</p>
                            </transition>
                        </div>
                    </div>
                    <div class="row">
                        <h5 class="col-md-12 page-header">ENDEREÇO</h5>
                    </div>
                    <div class="row">
                        <div class="col-md-8 form-group float-label-control">
                            <label for="">Rua</label>
                            <input data-vv-as="Rua" type="text" class="form-control" name="rua" v-model="form.endereco_rua" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('rua')">{{ errors.first('rua') }}</p>
                            </transition>
                        </div>
                        <div class="col-md-4 form-group float-label-control">
                            <label for="">Número</label>
                            <input data-vv-as="Numero" v-validate="'alpha_num'" type="text" class="form-control" name="numero" v-model="form.endereco_numero" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('numero')">{{ errors.first('numero') }}</p>
                            </transition>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12 form-group float-label-control">
                            <label for="">Complemento</label>
                            <input data-vv-as="Complemento" type="text" class="form-control" name="complemento" v-model="form.endereco_complemento">
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('complemento')">{{ errors.first('complemento') }}</p>
                            </transition>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-8 form-group float-label-control">
                            <label for="">Bairro</label>
                            <input data-vv-as="Bairro" v-validate="'alpha_spaces'" type="text" class="form-control" name="bairro" v-model="form.endereco_bairro" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('bairro')">{{ errors.first('bairro') }}</p>
                            </transition>
                        </div>
                        <div class="col-md-4 form-group float-label-control">
                            <label for="">CEP</label>
                            <input data-vv-as="CEP" type="numeric" maxlength="8" class="form-control" name="cep" v-model="form.endereco_cep" required="">
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('cep')">{{ errors.first('cep') }}</p>
                            </transition>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-9 form-group float-label-control">
                            <label for="">Cidade</label>
                            <input data-vv-as="Cidade" v-validate="'alpha_spaces'" type="text" class="form-control" name="cidade" v-model="form.endereco_cidade" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('cidade')">{{ errors.first('cidade') }}</p>
                            </transition>
                        </div>
                        <div class="col-md-3 form-group float-label-control">
                            <label for="">Estado</label>
                                <select class="form-control" v-model="form.endereco_estado">
                                    <option :value="form.endereco_estado" selected="selected">{{form.endereco_estado}}</option>
                                    <option v-if="form.endereco_estado != 'AC'" value='AC'>AC</option>
                                    <option v-if="form.endereco_estado != 'AL'" value='AL'>AL</option>
                                    <option v-if="form.endereco_estado != 'AP'" value='AP'>AP</option>
                                    <option v-if="form.endereco_estado != 'AM'" value='AM'>AM</option>
                                    <option v-if="form.endereco_estado != 'BA'" value='BA'>BA</option>
                                    <option v-if="form.endereco_estado != 'CE'" value='CE'>CE</option>
                                    <option v-if="form.endereco_estado != 'DF'" value='DF'>DF</option>
                                    <option v-if="form.endereco_estado != 'ES'" value='ES'>ES</option>
                                    <option v-if="form.endereco_estado != 'GO'" value='GO'>GO</option>
                                    <option v-if="form.endereco_estado != 'MA'" value='MA'>MA</option>
                                    <option v-if="form.endereco_estado != 'MT'" value='MT'>MT</option>
                                    <option v-if="form.endereco_estado != 'MS'" value='MS'>MS</option>
                                    <option v-if="form.endereco_estado != 'MG'" value='MG'>MG</option>
                                    <option v-if="form.endereco_estado != 'PA'" value='PA'>PA</option>
                                    <option v-if="form.endereco_estado != 'PB'" value='PB'>PB</option>
                                    <option v-if="form.endereco_estado != 'PR'" value='PR'>PR</option>
                                    <option v-if="form.endereco_estado != 'PE'" value='PE'>PE</option>
                                    <option v-if="form.endereco_estado != 'PI'" value='PI'>PI</option>
                                    <option v-if="form.endereco_estado != 'RJ'" value='RJ'>RJ</option>
                                    <option v-if="form.endereco_estado != 'RN'" value='RN'>RN</option>
                                    <option v-if="form.endereco_estado != 'RS'" value='RS'>RN</option>
                                    <option v-if="form.endereco_estado != 'RO'" value='RO'>RO</option>
                                    <option v-if="form.endereco_estado != 'RR'" value='RR'>RR</option>
                                    <option v-if="form.endereco_estado != 'SC'" value='SC'>SC</option>
                                    <option v-if="form.endereco_estado != 'SP'" value='SP'>SP</option>
                                    <option v-if="form.endereco_estado != 'SE'" value='SE'>SE</option>
                                    <option v-if="form.endereco_estado != 'TO'" value='TO'>TO</option>
                                </select>
                        </div>
                    </div>
                    <div class="row">
                        <h5 class="col-md-12 page-header">CONTATO</h5>
                    </div>
                    <div class="row">
                        <div class="col-md-2 form-group float-label-control">
                            <label for="">DDD</label>
                            <input data-vv-as="DDD"
                                   class="form-control" type="numeric" maxlength="2" name="ddd" v-model="form.telefone_ddd">
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX" required>
                                <p class="alert" v-if="errors.has('ddd')">{{ errors.first('ddd') }}</p>
                            </transition>
                        </div>
                        <div class=" col-md-8 form-group float-label-control">
                            <label for="">Telefone</label>
                            <input v-mask="['####-####', '#####-####']" data-vv-as="Telefone" type="text" class="form-control" name="telefone" v-model="form.telefone_numero" required>
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('telefone')">{{ errors.first('telefone') }}</p>
                            </transition>
                        </div>
                        <div class="col-md-2 form-group float-label-control">
                            <label for="">Ramal</label>
                            <input data-vv-as="Ramal" type="text" class="form-control" name="ramal" v-model="form.telefone_ramal">
                            <transition name="alert-in" enter-active-class="animated flipInX" leave-active-class="animated flipOutX">
                                <p class="alert" v-if="errors.has('ramal')">{{ errors.first('ramal') }}</p>
                            </transition>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12">
                            <button class="btn btn-lg btn-primary btn-block" type="submit">
                                Atualizar
                            </button>
                        </div>
                    </div>
                  </form>
                </div>
            </div>
            <!-- END: Formulario de contato -->

            <!-- BEGIN: Contrato -->
            <div role="tabpanel" class="tab-pane fade" id="contrato" aria-labelledby="contrato-tab">
                <div class="row">
                    <div class="col-md-12">
                        <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
                          <li class="nav-item">
                            <a class="nav-link active" id="pills-pt-tab" data-toggle="pill" href="#pills-pt" role="tab" aria-controls="pills-pt" aria-selected="true">pt-br</a>
                          </li>
                          <li class="nav-item">
                            <a class="nav-link" id="pills-tn-tab" data-toggle="pill" href="#pills-en" role="tab" aria-controls="pills-en" aria-selected="false">en-us</a>
                          </li>
                        </ul>
                    </div>
                </div>
                &nbsp;
                <div class="row">
                    <div class="col-md-12">
                        <div class="tab-content" id="pills-tabContent">
                          <div role="tabpanel" class="tab-pane active" id="pills-pt">
                            <div v-html="getContrato"></div>
                          </div>
                          <div role="tabpanel" class="tab-pane" id="pills-en">
                              <div v-html="getContratoEn"></div>
                          </div>
                        </div>
                    </div>
                </div>
                <div class='row'>
                  <form role="form" @submit.prevent="updateAssinaContrato">
                    <button v-if='!contrato_assinado' class="btn btn-success" type="submit">Assinar</button>
                  </form>
                </div>
            </div>
            <!-- END: Contrato -->
        </div>
    </div>
</template>

<script>
import Participante from '@/api/Participante'
import Contrato from '@/api/Contrato'
import portugues from 'vee-validate/dist/locale/pt_BR'

export default{
  data () {
    return {
      asn: this.$route.params.asn,
      asn_uuid: '',
      ix: this.$route.params.ix,
      contrato_assinado: true,
      info_contrato: {
        asn: null,
        cnpj: '',
        razao_social: '',
        responsavel: '',
        endereco_rua: '',
        endereco_numero: '',
        endereco_complemento: '',
        endereco_bairro: '',
        endereco_cep: '',
        endereco_cidade: '',
        endereco_estado: '',
        telefone_ddd: '',
        telefone_numero: '',
        telefone_ramal: ''
      },
      form: {
        asn: null,
        cnpj: '',
        razao_social: '',
        responsavel: '',
        endereco_rua: '',
        endereco_numero: '',
        endereco_complemento: '',
        endereco_bairro: '',
        endereco_cep: '',
        endereco_cidade: '',
        endereco_estado: '',
        telefone_ddd: '',
        telefone_numero: '',
        telefone_ramal: ''
      },
      template_contrato: '',
      template_contrato_en: ''
    }
  },
  computed: {
    getContrato: function () {
      var contrato = this.template_contrato
      contrato = contrato.replace(`{razao_social}`, this.info_contrato.razao_social)
      contrato = contrato.replace(`{cnpj}`, this.info_contrato.cnpj)
      contrato = contrato.replace(`{endereco_rua}`, this.info_contrato.endereco_rua)
      contrato = contrato.replace(`{endereco_numero}`, this.info_contrato.endereco_numero)
      contrato = contrato.replace(`{endereco_complemento}`, this.info_contrato.endereco_complemento)
      contrato = contrato.replace(`{endereco_cidade}`, this.info_contrato.endereco_cidade)
      contrato = contrato.replace(`{endereco_estado}`, this.info_contrato.endereco_estado)
      contrato = contrato.replace(`{endereco_cep}`, this.info_contrato.endereco_cep)
      contrato = contrato.replace(`{responsavel}`, this.info_contrato.responsavel)
      return contrato
    },
    getContratoEn: function () {
      var contrato = this.template_contrato_en
      contrato = contrato.replace(`{razao_social}`, this.info_contrato.razao_social)
      contrato = contrato.replace(`{cnpj}`, this.info_contrato.cnpj)
      contrato = contrato.replace(`{endereco_rua}`, this.info_contrato.endereco_rua)
      contrato = contrato.replace(`{endereco_numero}`, this.info_contrato.endereco_numero)
      contrato = contrato.replace(`{endereco_complemento}`, this.info_contrato.endereco_complemento)
      contrato = contrato.replace(`{endereco_cidade}`, this.info_contrato.endereco_cidade)
      contrato = contrato.replace(`{endereco_estado}`, this.info_contrato.endereco_estado)
      contrato = contrato.replace(`{endereco_cep}`, this.info_contrato.endereco_cep)
      contrato = contrato.replace(`{responsavel}`, this.info_contrato.responsavel)
      return contrato
    }
  },
  methods: {
    async getContratoAPI () {
      let response = await Contrato.getContratoVigente({ asn: this.asn, ix: this.ix, assinado: true })
      if (response.data.length !== 0) {
        this.contrato_uuid = response.data[0].uuid
        this.template_contrato = response.data[0].template_pt
        this.template_contrato_en = response.data[0].template_en
      } else {
        this.contrato_assinado = false
        response = await Contrato.getContratoVigente({ asn: this.asn, ix: this.ix, assinado: false })
        this.contrato_uuid = response.data[0].uuid
        this.template_contrato = response.data[0].template_pt
        this.template_contrato_en = response.data[0].template_en
      }
    },
    async getParticipanteAPI () {
      const response = await Participante.getParticipante({ asn: this.asn, ix: this.ix })

      this.asn_uuid = response.data[0].uuid

      this.info_contrato.asn = this.form.asn = response.data[0].asn
      this.info_contrato.endereco_bairro = this.form.endereco_bairro = response.data[0].endereco_bairro
      this.info_contrato.cnpj = this.form.cnpj = response.data[0].cnpj
      this.info_contrato.endereco_cidade = this.form.endereco_cidade = response.data[0].endereco_cidade
      this.info_contrato.razao_social = this.form.razao_social = response.data[0].razao_social
      this.info_contrato.responsavel = this.form.responsavel = response.data[0].responsavel
      this.info_contrato.endereco_rua = this.form.endereco_rua = response.data[0].endereco_rua
      this.info_contrato.endereco_numero = this.form.endereco_numero = response.data[0].endereco_numero
      this.info_contrato.endereco_complemento = this.form.endereco_complemento = response.data[0].endereco_complemento
      this.info_contrato.endereco_cep = this.form.endereco_cep = response.data[0].endereco_cep
      this.info_contrato.endereco_estado = this.form.endereco_estado = response.data[0].endereco_estado
      this.info_contrato.telefone_ddd = this.form.telefone_ddd = response.data[0].telefone_ddd
      this.info_contrato.telefone_numero = this.form.telefone_numero = response.data[0].telefone_numero
      this.info_contrato.telefone_ramal = this.form.telefone_ramal = response.data[0].telefone_ramal
    },
    async updateParticipante (e) {
      e.preventDefault()
      this.form.cnpj = this.form.cnpj.replace(/[^0-9]+/g, '')
      const data = this.form
      const response = await Participante.updateParticipante({ asn: this.asn_uuid, data })
      if (response === 'Atualizado com sucesso') { // TODO: responsta do Participante.updateParticipante
        this.info_contrato = this.form
        alert('Atualizado com sucesso\n\nAtenção: É necessário assinar o contrato com os novos dados')
      } else {
        let errors = ''
        for (var errorMessage of response) {
          errors = errors + errorMessage['message']
        }
        alert(errors)
      }
      this.getContratoAPI()
    },
    async updateAssinaContrato (e) {
      e.preventDefault()
      await Contrato.patchAssinaContrato({ contrato_uuid: this.contrato_uuid }).then(response => {
        alert('Contrato assinado!')
      }).catch(error => {
        let message = error.response.data
        alert('Servidor fora do ar. Tente novamente em alguns instante\n\n' + message)
      })
      location.reload()
    }
  },
  created () {
    this.$validator.localize('pt_BR', {
      messages: portugues.messages
    })
    this.$validator.localize('pt_BR')
  },
  mounted () {
    this.getParticipanteAPI()
    this.getContratoAPI()
  }
}

</script>

<style scoped>
@import "https://cdn.jsdelivr.net/npm/animate.css@3.5.1";

  .alert {
    background: lightsalmon;
    font-weight: bold;
    display: inline-block;
    padding: 5px;
    margin-top: -5px;
  }
  .alert-in-enter-active{
      animation: bounce-in .5s;
  }
  .alert-in-leave-active{
      animation: bounce-in .5s reverse;
  }

  @keyframes bounce-in {
      0% {
          transform: scale(0);
      }
      50% {
          transform: scale(1.5);
      }
      100%{
          transform: scale(1);
      }
  }
</style>
