<template>
  <div id="app">
    <div class="container">
      <Header />
      <Content />
      <Footer />
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import Header from '@/components/Header.vue'
import Content from '@/components/Content.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'app',
  components: {
    Header,
    Content,
    Footer
  }
}
</script>
<style lang="scss">
  @import './assets/scss/main.scss'
</style>
