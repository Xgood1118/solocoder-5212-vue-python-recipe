import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据概览', icon: 'DataLine' },
      },
      {
        path: 'recipes',
        name: 'Recipes',
        component: () => import('@/views/recipes/RecipeList.vue'),
        meta: { title: '菜谱管理', icon: 'Food' },
      },
      {
        path: 'recipes/new',
        name: 'RecipeNew',
        component: () => import('@/views/recipes/RecipeEdit.vue'),
        meta: { title: '新建菜谱', icon: 'Plus' },
        hidden: true,
      },
      {
        path: 'recipes/:id/edit',
        name: 'RecipeEdit',
        component: () => import('@/views/recipes/RecipeEdit.vue'),
        meta: { title: '编辑菜谱', icon: 'Edit' },
        hidden: true,
      },
      {
        path: 'recipes/:id/preview',
        name: 'RecipePreview',
        component: () => import('@/views/recipes/RecipePreview.vue'),
        meta: { title: '菜谱预览', icon: 'View' },
        hidden: true,
      },
      {
        path: 'ingredients',
        name: 'Ingredients',
        component: () => import('@/views/ingredients/IngredientList.vue'),
        meta: { title: '食材库', icon: 'Vegetable' },
      },
      {
        path: 'feedback',
        name: 'Feedback',
        component: () => import('@/views/feedback/FeedbackList.vue'),
        meta: { title: '用户反馈', icon: 'ChatDotRound' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
