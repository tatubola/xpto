<template>
  <div>
      <li class="nav-item">
        <router-link class="nav-link" :to="{name: 'services', params: { asn: asn, ix: ix }}">
          <a>Serviços</a>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" :to="{name: 'invoice', params: { asn: asn, ix: ix }}">
          <a>Fatura</a>
        </router-link>
      <li class="nav-item">
        <router-link class="nav-link" :to="{name: 'conta', params: { asn: asn, ix: ix }}">
          <a>Conta</a>
        </router-link>
      </li>
    <li class="nav-divider"></li>
  </div>
</template>

<script>
export default {
  data () {
    return {
      asn: this.$route.params.asn,
      ix: this.$route.params.ix
    }
  }
}

</script>

<style type="text/scss" scoped>
  .nav-sidebar {
    width: 100%;
    padding: 8px 0;
    border-right: 1px solid #ddd;
  }

  .nav-sidebar a {
    color: #333;
    -webkit-transition: all 0.08s linear;
    -moz-transition: all 0.08s linear;
    -o-transition: all 0.08s linear;
    transition: all 0.08s linear;
    -webkit-border-radius: 4px 0 0 4px;
    -moz-border-radius: 4px 0 0 4px;
    border-radius: 4px 0 0 4px;
  }

  .nav-sidebar .router-link-exact-active a {
    cursor: default;
    color: #fff;
    text-shadow: 1px 1px 1px #666;
  }

  .nav-sidebar .router-link-exact-active {
    cursor: default;
    background-color: #d66902;
  }

  .nav-sidebar .router-link-exact-active a:hover {
    background-color: #d66902;
  }

  .nav-sidebar .text-overflow a,
  .nav-sidebar .text-overflow .media-body {
    white-space: nowrap;
    overflow: hidden;
    -o-text-overflow: ellipsis;
    text-overflow: ellipsis;
  }

  .nav .nav-divider {
    height: 1px;
    margin: 9px 0;
    overflow: hidden;
    background-color: #ddd;
  }

  li:hover {
    background: #e9ecef;
  }
</style>
