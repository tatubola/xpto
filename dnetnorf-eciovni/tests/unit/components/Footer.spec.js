import Vue from 'vue'
import Footer from '@/components/Footer.vue'

// helper function that mounts and returns the rendered text
function getRenderedText (Component, propsData) {
  const Constructor = Vue.extend(Component)
  const vm = new Constructor({ propsData: propsData }).$mount()
  return vm.$el.textContent
}

function getHTMLListOfLogos (Component, idLogo) {
  const Constructor = Vue.extend(Component)
  const vm = new Constructor().$mount()
  return vm.$el.querySelector(idLogo).innerHTML
}

describe('Footer', () => {
  it('renders static info correctly', () => {
    expect(getRenderedText(Footer)).toContain('NIC.BR - Núcleo de Informação e Coordenação do Ponto BR')
    expect(getRenderedText(Footer)).toContain('CNPJ: 05.506.560/0001-36')
  })

  it('renders static images with link correctly', () => {
    const listLogoHtml = getHTMLListOfLogos(Footer, '.logos-footer')
    expect(listLogoHtml).toContain('<a href="https://cgi.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://nic.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://registro.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://cert.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://cetic.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://ceptro.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://ceweb.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://ix.br"></a>')
    expect(listLogoHtml).toContain('<a href="https://www.w3c.br/Home/WebHome"></a>')
  })
})
