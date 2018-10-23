import Vue from 'vue'
import Header from '@/components/Header.vue'

// helper function that mounts and returns the rendered text
function getRenderedText (Component) {
  const Constructor = Vue.extend(Component)
  const vm = new Constructor().$mount()
  return vm.$el.textContent
}

function getInnerHtml (Component, elementToSelect) {
  const Constructor = Vue.extend(Component)
  const vm = new Constructor().$mount()
  return vm.$el.querySelector(elementToSelect).innerHTML
}

describe('Header', () => {
  it('renders Nic.br and IX.br logos and links', () => {
    const divRowWithImage = getInnerHtml(Header, '.col-md-4')
    expect(divRowWithImage).toContain('<img src="../assets/logo-ix-br.png" alt="Logo Nic.br / Ix.br">')
    expect(divRowWithImage).toContain('<a href="https://nic.br" id="link-nic" style="background: url(about:blank);">&nbsp;</a>')
    expect(divRowWithImage).toContain('<a href="https://ix.br" id="link-ix" style="background: url(about:blank);">&nbsp;</a>')
  })

  it('shows Logout button', () => {
    const divButtons = getInnerHtml(Header, '.header-buttons')
    expect(divButtons).toContain('<button class="btn btn-light"><span>Logout</span></button>')
  })

  it('renders static texts correctly', () => {
    const renderedTexts = getRenderedText(Header)
    expect(renderedTexts).toContain('Dashboard')
    expect(renderedTexts).toContain('My Account')
    expect(renderedTexts).toContain('Recommendations')
    expect(renderedTexts).toContain('BGP Looking Glass')
    expect(renderedTexts).toContain('Invoice')
  })

  it('checks if Invoice is active (bold)', () => {
    const someActive = getInnerHtml(Header, '.active')
    expect(someActive).toBe('Invoice')
  })
})
