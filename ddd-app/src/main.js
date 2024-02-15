// import { createApp } from 'vue'
// import App from './App.vue'

// createApp(App).mount('#app')

import { createApp } from 'vue'
import CarbonVue3 from '@carbon/vue';
import CarbonComponentsVue from "@carbon/vue";
import App from './App.vue'
const app = createApp(App)
app.use(CarbonVue3);
app.use(CarbonComponentsVue);
app.mount('#app');