<template>
  <el-container class="layout-container no-print">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="28"><Food /></el-icon>
        <span>菜谱管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#ffd04b"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item :index="'/' + route.path">
            <el-icon>
              <component :is="iconMap[route.meta.icon]" />
            </el-icon>
            <span>{{ route.meta.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">
          <el-icon size="20" style="margin-right: 8px"><Location /></el-icon>
          <span>{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-tag type="info">编辑团队</el-tag>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Food, DataLine, Edit, Plus, View, ChatDotRound, Apple, Location,
  Star, CircleCheck, Trophy, Grape, Clock, User, List, Printer
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const iconMap = {
  DataLine: markRaw(DataLine),
  Food: markRaw(Food),
  Apple: markRaw(Apple),
  ChatDotRound: markRaw(ChatDotRound),
  Edit: markRaw(Edit),
  Plus: markRaw(Plus),
  View: markRaw(View),
  Star: markRaw(Star),
  CircleCheck: markRaw(CircleCheck),
  Trophy: markRaw(Trophy),
  Grape: markRaw(Grape),
  Clock: markRaw(Clock),
  User: markRaw(User),
  List: markRaw(List),
  Printer: markRaw(Printer),
  Location: markRaw(Location),
}

const menuRoutes = computed(() => {
  const routes = router.options.routes[0].children
  return routes.filter(r => !r.meta?.hidden)
})

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '')
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #2b3648;
  border-bottom: 1px solid #1f2d3d;
}

.logo span {
  white-space: nowrap;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
