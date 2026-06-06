<template>
  <div class="recipe-preview">
    <div class="no-print">
      <el-page-header @back="$router.back()" content="菜谱预览">
        <template #extra>
          <el-button @click="handlePrint">
            <el-icon><Printer /></el-icon>
            打印菜谱
          </el-button>
        </template>
      </el-page-header>
    </div>

    <div class="preview-content" v-loading="loading">
      <div v-if="recipe" class="recipe-card">
        <div class="recipe-header">
          <h1 class="recipe-name">{{ recipe.name }}</h1>
          <div class="recipe-meta">
            <span class="meta-item">
              <el-icon><Location /></el-icon>
              {{ cuisineIcon }} {{ recipe.cuisine }}
            </span>
            <span class="meta-item">
              <el-icon><Trophy /></el-icon>
              难度：{{ recipe.difficulty }}
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              约 {{ recipe.cookTime }} 分钟
            </span>
            <span class="meta-item">
              <el-icon><User /></el-icon>
              适合 {{ recipe.servings }} 人
            </span>
          </div>
        </div>

        <div class="recipe-image" v-if="recipe.imageUrl">
          <el-image :src="recipe.imageUrl" fit="cover" style="width: 100%; height: 300px; border-radius: 8px" />
        </div>

        <div class="nutrition-section" v-if="nutrition">
          <h3><el-icon><Grape /></el-icon> 营养信息汇总（整份）</h3>
          <el-row :gutter="12">
            <el-col :span="6">
              <div class="nutri-item">
                <div class="nutri-value">{{ nutrition.calories }}</div>
                <div class="nutri-label">卡路里 (kcal)</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="nutri-item">
                <div class="nutri-value">{{ nutrition.protein }}</div>
                <div class="nutri-label">蛋白质 (g)</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="nutri-item">
                <div class="nutri-value">{{ nutrition.fat }}</div>
                <div class="nutri-label">脂肪 (g)</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="nutri-item">
                <div class="nutri-value">{{ nutrition.carbs }}</div>
                <div class="nutri-label">碳水 (g)</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="ingredients-section">
          <h3><el-icon><Food /></el-icon> 食材清单</h3>
          <div class="ingredient-columns">
            <div class="ing-col">
              <h4>主料</h4>
              <ul v-if="recipe.mainIngredients && recipe.mainIngredients.length">
                <li v-for="(ing, idx) in recipe.mainIngredients" :key="idx">
                  <span class="ing-name">{{ ing.name }}</span>
                  <span class="ing-amount">
                    {{ ing.amount }}{{ ing.unit }}
                    <el-tag v-if="ing.optional" size="small" type="info" style="margin-left: 6px">可选</el-tag>
                  </span>
                </li>
              </ul>
              <p v-else class="empty-text">无</p>
            </div>
            <div class="ing-col">
              <h4>辅料</h4>
              <ul v-if="recipe.auxIngredients && recipe.auxIngredients.length">
                <li v-for="(ing, idx) in recipe.auxIngredients" :key="idx">
                  <span class="ing-name">{{ ing.name }}</span>
                  <span class="ing-amount">
                    {{ ing.amount }}{{ ing.unit }}
                    <el-tag v-if="ing.optional" size="small" type="info" style="margin-left: 6px">可选</el-tag>
                  </span>
                </li>
              </ul>
              <p v-else class="empty-text">无</p>
            </div>
            <div class="ing-col">
              <h4>调料</h4>
              <ul v-if="recipe.seasonings && recipe.seasonings.length">
                <li v-for="(ing, idx) in recipe.seasonings" :key="idx">
                  <span class="ing-name">{{ ing.name }}</span>
                  <span class="ing-amount">
                    {{ ing.amount }}{{ ing.unit }}
                    <el-tag v-if="ing.optional" size="small" type="info" style="margin-left: 6px">可选</el-tag>
                  </span>
                </li>
              </ul>
              <p v-else class="empty-text">无</p>
            </div>
          </div>
        </div>

        <div class="steps-section">
          <h3><el-icon><List /></el-icon> 烹饪步骤</h3>
          <div class="step-list">
            <div v-for="(step, idx) in recipe.steps" :key="idx" class="step-item">
              <div class="step-number">{{ idx + 1 }}</div>
              <div class="step-content">
                <p class="step-desc">{{ step.description }}</p>
                <div class="step-meta">
                  <span v-if="step.duration"><el-icon><Clock /></el-icon> {{ step.duration }} 分钟</span>
                </div>
                <div class="step-tip" v-if="step.tip">
                  <el-icon><ChatDotRound /></el-icon>
                  <strong>小贴士：</strong>{{ step.tip }}
                </div>
                <div v-if="step.images && step.images.length" class="step-images">
                  <el-image
                    v-for="(img, iIdx) in step.images"
                    :key="iIdx"
                    :src="img"
                    fit="cover"
                    class="step-image"
                    :preview-src-list="step.images"
                    :initial-index="iIdx"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="footer-note">
          <p>— 家常菜谱管理系统 —</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  Printer, Location, Trophy, Clock, User, Grape, Food, List, ChatDotRound
} from '@element-plus/icons-vue'
import { getRecipeDetail, getRecipeNutrition } from '@/api/recipe'
import { getConstants } from '@/api/common'

const route = useRoute()
const loading = ref(false)
const recipe = ref(null)
const nutrition = ref(null)
const cuisineIcons = ref({})

const cuisineIcon = computed(() => {
  if (!recipe.value) return '🍽️'
  return cuisineIcons.value[recipe.value.cuisine] || '🍽️'
})

function handlePrint() {
  window.print()
}

async function loadData() {
  const id = route.params.id

  if (id === 'draft') {
    const draft = localStorage.getItem('recipe_preview')
    if (draft) {
      recipe.value = JSON.parse(draft)
    }
    return
  }

  loading.value = true
  try {
    recipe.value = await getRecipeDetail(id)
    nutrition.value = await getRecipeNutrition(id)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const constants = await getConstants()
    cuisineIcons.value = constants.cuisineIcons || {}
  } catch (e) {}
  loadData()
})
</script>

<style scoped>
.recipe-preview {
  padding-bottom: 40px;
}

.preview-content {
  margin-top: 20px;
}

.recipe-card {
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.recipe-header {
  text-align: center;
  margin-bottom: 24px;
}

.recipe-name {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.recipe-meta {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
  color: #606266;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.recipe-image {
  margin-bottom: 28px;
}

.recipe-image :deep(img) {
  border-radius: 8px;
}

h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
  display: inline-block;
}

h4 {
  font-size: 15px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.nutrition-section {
  margin-bottom: 28px;
}

.nutri-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.nutri-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.nutri-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.ingredients-section {
  margin-bottom: 28px;
}

.ingredient-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.ing-col ul {
  list-style: none;
  padding: 0;
}

.ing-col li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px dashed #ebeef5;
  font-size: 14px;
}

.ing-name {
  color: #303133;
}

.ing-amount {
  color: #909399;
  font-size: 13px;
}

.empty-text {
  color: #c0c4cc;
  font-size: 13px;
}

.steps-section {
  margin-bottom: 28px;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  gap: 16px;
}

.step-number {
  width: 36px;
  height: 36px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  background: #f5f7fa;
  padding: 14px 18px;
  border-radius: 8px;
}

.step-desc {
  font-size: 15px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 8px;
}

.step-meta {
  font-size: 13px;
  color: #909399;
  display: flex;
  gap: 4px;
  align-items: center;
}

.step-tip {
  margin-top: 10px;
  padding: 10px 12px;
  background: #fdf6ec;
  border-radius: 6px;
  font-size: 13px;
  color: #e6a23c;
  line-height: 1.5;
}

.step-images {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.step-image {
  width: 120px;
  height: 120px;
  border-radius: 6px;
  cursor: pointer;
}

.footer-note {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

@media print {
  .no-print {
    display: none !important;
  }

  .recipe-card {
    box-shadow: none;
    padding: 20px;
  }

  .recipe-name {
    font-size: 28px;
  }

  .step-image {
    page-break-inside: avoid;
  }
}
</style>
