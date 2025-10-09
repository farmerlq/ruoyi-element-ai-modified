// 引入ElementPlus所有图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import ElementPlus from 'element-plus';
import { ElMessage } from 'element-plus';
import { createApp } from 'vue';
import App from './App.vue';
import router from './routers';
import store from './stores';
import './styles/index.scss';
import 'element-plus/dist/index.css';

const app = createApp(App);

app.use(router);
app.use(ElementPlus);
// 注册ElementPlus所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}
app.use(store);

app.mount('#app');
