import Vue from 'vue'
import { shallowMount, RouterLinkStub } from '@vue/test-utils'
import Content from '@/components/Content.vue'

function getElement (Component, elementToSelect) {
  const routerView = {
    name: 'router-view',
    render: h => h('div')
  }
  Vue.component('router-view', routerView)
  const wrapper = shallowMount(Component, {
    stubs: {
      RouterLink: RouterLinkStub
    }
  })
  return wrapper.find(elementToSelect).element
}

describe('Content', () => {
  it('Creates its links correctly', () => {
    const divElement = getElement(Content, '#internal')
    expect(divElement._prevClass).toBe('row mt-2')
  })
})
