import { createRouter, createWebHistory } from 'vue-router'

import FileSelect from './views/FileSelect.vue'
import Progress from './views/Progress.vue'
import Overview from './views/Overview.vue'
import RackDetail from './views/RackDetail.vue'
import CellDetail from './views/CellDetail.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/files' },
    { path: '/files', component: FileSelect },
    { path: '/progress', component: Progress },
    { path: '/overview', component: Overview },
    { path: '/rack/:id', component: RackDetail, props: true },
    { path: '/cell/:rack/:module/:cell', component: CellDetail, props: true }
  ]
})
