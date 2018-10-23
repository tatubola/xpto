import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import InfoConta from './views/InfoConta.vue'
import Services from './views/Services.vue'
import Invoice from './views/Invoice.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/:asn',
      name: 'home',
      component: Home
    },
    {

      path: '/:asn/:ix/conta',
      name: 'conta',
      component: InfoConta
    },
    {
      path: '/:asn/:ix/services',
      name: 'services',
      component: Services
    },
    {
      path: '/:asn/:ix/invoice',
      name: 'invoice',
      component: Invoice
    }
  ]
})
