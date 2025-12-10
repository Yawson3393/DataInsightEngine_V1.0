import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

import 'ant-design-vue/dist/reset.css'
import Antd from 'ant-design-vue'

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(Antd)

app.mount('#app')
