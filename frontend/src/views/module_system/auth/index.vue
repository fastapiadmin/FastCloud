<template>
  <div class="login-container">
    <!-- 右侧切换主题、语言按钮  -->
    <div class="action-bar">
      <el-tooltip :content="t('login.themeToggle')" placement="bottom">
        <CommonWrapper>
          <ThemeSwitch />
        </CommonWrapper>
      </el-tooltip>
      <el-tooltip :content="t('login.languageToggle')" placement="bottom">
        <CommonWrapper>
          <LangSelect size="text-20px" />
        </CommonWrapper>
      </el-tooltip>
    </div>
    <!-- 登录页主体 -->
    <div flex-1 flex-center>
      <div
        class="p-2xl w-full h-auto sm:w-450px border-rd-10px shadow-[var(--el-box-shadow-light)] backdrop-blur-3px"
      >
        <div w-full flex flex-col items-center>
          <!-- logo -->
          <div class="logo-container">
            <img src="/favicon.png" alt="Logo" style="display: block; width: 140px; height: auto" />
          </div>

          <!-- 标题 -->
          <!-- 添加小图标用于显示提示信息 -->
          <div class="flex items-center justify-center mb-4">
            <el-tooltip :content="title + ' 是完全开源的权限管理系统'" placement="bottom">
              <el-icon class="cursor-help"><QuestionFilled /></el-icon>
            </el-tooltip>
            <div class="ml-2 text-xl font-bold">
              <el-badge :value="`v ${version}`" type="success">
                {{ title }}
              </el-badge>
            </div>
          </div>

          <!-- 组件切换 -->
          <transition name="fade-slide" mode="out-in">
            <component
              :is="formComponents[component]"
              v-model="component"
              v-model:preset-username="loginPreset.username"
              v-model:preset-password="loginPreset.password"
              class="w-90%"
            />
          </transition>
        </div>
      </div>
      <!-- 登录页底部版权 -->
      <el-text size="small" class="py-2.5! fixed bottom-0 text-center">
        <a href="https://github.com/fastapiadmin/FastCloud.git" target="_blank">
          Copyright © 2025-2026 service.fastapiadmin.com 版权所有 |
        </a>
        <a href="https://service.fastapiadmin.com" target="_blank">帮助 |</a>
        <a href="https://github.com/fastapiadmin/FastCloud/blob/master/LICENSE" target="_blank">
          隐私 |
        </a>
        <a href="https://github.com/fastapiadmin/FastCloud/blob/master/LICENSE" target="_blank">
          条款
        </a>
      </el-text>
    </div>
  </div>
</template>

<script setup lang="ts">
import CommonWrapper from "@/components/CommonWrapper/index.vue";
import ThemeSwitch from "@/components/ThemeSwitch/index.vue";
import { useSettingsStore } from "@/store/modules/settings.store";

const settingsStore = useSettingsStore();

const title = computed(() => settingsStore.title);
const version = computed(() => settingsStore.version);

type LayoutMap = "login" | "register" | "resetPwd";

const t = useI18n().t;

const component = ref<LayoutMap>("login"); // 切换显示的组件
const formComponents = {
  login: defineAsyncComponent(() => import("./components/Login.vue")),
  register: defineAsyncComponent(() => import("./components/Register.vue")),
  resetPwd: defineAsyncComponent(() => import("./components/ResetPwd.vue")),
};

// 预填登录信息（通过具名 v-model 双向绑定传递）
const loginPreset = reactive<{ username: string; password: string }>({
  username: "admin",
  password: "123456",
});
</script>

<style lang="scss" scoped>
.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  padding: 0;
  margin: 0;
  background-image: url(/background.svg);
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-bar {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 10;
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;

  @media (max-width: 480px) {
    top: 10px;
    right: auto;
    left: 10px;
  }

  @media (min-width: 640px) {
    top: 40px;
    right: 40px;
  }
}

/* fade-slide */
.fade-slide-leave-active,
.fade-slide-enter-active {
  transition: all 0.3s;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
