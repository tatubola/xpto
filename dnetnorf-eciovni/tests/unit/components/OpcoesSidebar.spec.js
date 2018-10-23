import OpcoesSidebar from '@/components/OpcoesSidebar.vue'
import { shallowMount, RouterLinkStub } from '@vue/test-utils'

var getWrapper = (Component, route) => {
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

describe('OpcoesSidebar.vue', () => {
  let route = {
    name: 'services',
    params: { asn: '22548', ix: 'ria' }
  }

  it('Garantir a ordem dos elementos', () => {
    const wrapper = getWrapper(OpcoesSidebar, route)
    const li = wrapper.findAll('li')

    expect(li.at(0).text()).toBe('Serviços')
    expect(li.at(1).text()).toBe('Fatura')
    expect(li.at(2).text()).toBe('Conta')
  })

  it('Garantir que criou os links corretamente', () => {
    const wrapper = getWrapper(OpcoesSidebar, route)
    const routerLink = wrapper.find(RouterLinkStub)

    expect(routerLink.props()['to'].name).toBe('services')
    expect(routerLink.props()['to'].params).toEqual(route.params)
  })
})
