<template>
    <div class="row mt-2" id="internal">
        <div class="col-sm-2">
            <Sidebar />
        </div>
        <div class="col-sm-10">
            <router-view/>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import Sidebar from '@/components/Sidebar.vue'

Vue.component('Sidebar', { template: '#sidebar' })

export default {
  name: 'internal',
  components: {
    Sidebar
  }
}
</script>
