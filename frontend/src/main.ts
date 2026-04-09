import { createApp } from "vue";
import App from "./App.vue";
import setupPlugins from "@/plugins";
import { createTerminal } from "vue-web-terminal";

// 暗黑主题样式
import "element-plus/theme-chalk/dark/css-vars.css";
import "element-plus/dist/index.css";
// 暗黑模式自定义变量
import "@/styles/dark/css-vars.css";
import "@/styles/index.scss";

import "uno.css";

// 过渡动画
import "animate.css";

const app = createApp(App);
// 注册插件
app.use(setupPlugins);
// 注册终端组件
app.use(createTerminal());

app.mount("#app");
