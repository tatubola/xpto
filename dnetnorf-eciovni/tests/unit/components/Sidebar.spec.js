import { shallowMount, RouterLinkStub } from '@vue/test-utils'
import Sidebar from '@/components/Sidebar.vue'
import OpcoesSidebar from '@/components/OpcoesSidebar.vue'

function getRenderedRoutersLinks (Component, route, store) {
  const wrapper = shallowMount(Component, {
    mocks: {
      $store: store,
      $route: route
    },
    stubs: {
      RouterLink: RouterLinkStub
    }
  })
  return wrapper
}

describe('Sidebar.vue', () => {
  let route = { name: 'services', params: { asn: '22548', ix: 'ria' } }
  let store = { state: { exibirOpcoes: false } }

  it('Garantir que criou os links corretamente', () => {
    const wrapper = getRenderedRoutersLinks(Sidebar, route, store)
    const routersLinks = wrapper.findAll(RouterLinkStub)
    expect(routersLinks.at(0).props()['to'].name).toBe('home')
  })

  it('Garantir que OpcoesSidebar *é* renderizado quando store.exibirOpcoes for `false`', () => {
    const wrapper = getRenderedRoutersLinks(Sidebar, route, store)
    expect(wrapper.contains(OpcoesSidebar)).toBe(true)
  })

  it('Garantir que OpcoesSidebar *não é* renderizado quando store.exibirOpcoes for `true`', () => {
    store.state.exibirOpcoes = true
    const wrapper = getRenderedRoutersLinks(Sidebar, route, store)
    expect(wrapper.contains(OpcoesSidebar)).toBe(false)
  })
})
