import { shallowMount, RouterLinkStub } from '@vue/test-utils'
import Home from '@/views/Home.vue'

// helper function that mounts and returns the rendered text
function getWrapper (Component, route) {
  const wrapper = shallowMount(Component, {
    mocks: {
      $route: route
    },
    stubs: {
      RouterLink: RouterLinkStub
    }
  })
  return wrapper
}

describe('Home.vue', () => {
  let route = { name: 'home', params: { asn: '22548' } }

  it('Renderiza a informação estatica corretamente', () => {
    const wrapper = getWrapper(Home, route)
    expect(wrapper.vm.$el.textContent).toContain('Lista de IX')
  })

  it('Define os dados padrão corretamente', () => {
    expect(typeof Home.data).toBe('function')
  })

  it('Processa o conteúdo correto dos dados', () => {
    const wrapper = getWrapper(Home, route)
    wrapper.setData({
      ix: [
        { cidade: 'Sao Paulo', codigo: 'sp1', estado: 'SP', ix_id: 10, nome_curto: 'saopaulo.sp', nome_longo: 'Sao Paulo - SP' },
        { cidade: 'Santa Maria', codigo: 'ria', estado: 'RS', ix_id: 20, nome_curto: 'santamaria.rs', nome_longo: 'Santa Maria - RS' }
      ]
    })
    // const routersLinks = wrapper.findAll(RouterLinkStub)
    expect(wrapper.text()).toContain('Sao Paulo - SP')
    expect(wrapper.text()).toContain('Santa Maria - RS')
  })
})
