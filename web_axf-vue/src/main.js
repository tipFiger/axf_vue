// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import axios from 'axios'
// import VueAxios from 'vue-axios'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css';
import router from './router'

import './global.css';

// Vue.set(VueAxios, axios)

const ajax = axios.create({
  baseURL: 'http://47.112.115.185:8000'
})
Vue.config.productionTip = false
Vue.prototype.axios = ajax

Vue.use(ElementUI)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
