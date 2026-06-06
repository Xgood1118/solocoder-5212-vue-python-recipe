<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon icon-blue">
              <el-icon size="28"><Food /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalRecipes || 0 }}</div>
              <div class="stat-label">总菜谱数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon icon-green">
              <el-icon size="28"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.publishedRecipes || 0 }}</div>
              <div class="stat-label">已发布</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon icon-orange">
              <el-icon size="28"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingFeedback || 0 }}</div>
              <div class="stat-label">待审评价</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon icon-purple">
              <el-icon size="28"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.last7DaysAvgRating || 0 }}</div>
              <div class="stat-label">近7天均分</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近7天发布趋势</span>
            </div>
          </template>
          <div class="pub-trend">
            <div class="trend-value">
              <span class="number">{{ stats.last7DaysPublished || 0 }}</span>
              <span class="unit">道</span>
            </div>
            <div class="trend-label">近 7 天新发布菜谱</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>食材使用排行 TOP 10</span>
            </div>
          </template>
          <el-table :data="ingredientRank" size="small" :show-header="false">
            <el-table-column type="index" width="40" align="center">
              <template #default="{ $index }">
                <el-tag v-if="$index < 3" :type="['danger', 'warning', 'success'][$index]" size="small">
                  {{ $index + 1 }}
                </el-tag>
                <span v-else style="color: #909399">{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="食材" />
            <el-table-column prop="category" width="80" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" width="80" align="right">
              <template #default="{ row }">
                <span style="font-weight: bold; color: #409eff">{{ row.count }}</span>
                <span style="color: #909399; font-size: 12px"> 次</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/recipes/new')">
              <el-icon style="margin-right: 6px"><Plus /></el-icon>
              新建菜谱
            </el-button>
            <el-button size="large" @click="$router.push('/ingredients')">
              <el-icon style="margin-right: 6px"><Vegetable /></el-icon>
              食材库管理
            </el-button>
            <el-button size="large" @click="$router.push('/feedback')">
              <el-icon style="margin-right: 6px"><ChatDotRound /></el-icon>
              评价审核
            </el-button>
            <el-button size="large" type="success" @click="handleExport">
              <el-icon style="margin-right: 6px"><Download /></el-icon>
              导出菜谱
            </el-button>
            <el-upload
              :show-file-list="false"
              accept=".json"
              :before-upload="handleImport"
              style="display: inline-block; margin-left: 10px"
            >
              <el-button size="large" type="warning">
                <el-icon style="margin-right: 6px"><Upload /></el-icon>
                导入菜谱
              </el-button>
            </el-upload>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Food, CircleCheck, ChatDotRound, Star, Plus, Vegetable, Download, Upload
} from '@element-plus/icons-vue'
import { getOverviewStats, getIngredientRank } from '@/api/common'
import { exportRecipes, importRecipes } from '@/api/recipe'

const router = useRouter()
const stats = ref({})
const ingredientRank = ref([])

async function loadData() {
  try {
    stats.value = await getOverviewStats()
  } catch (e) {
    console.error(e)
  }
  try {
    ingredientRank.value = await getIngredientRank(10)
  } catch (e) {
    console.error(e)
  }
}

function handleExport() {
  exportRecipes().then(data => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `recipes_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  })
}

function handleImport(file) {
  ElMessageBox.confirm(
    '导入将新增菜谱数据，确定要导入吗？',
    '确认导入',
    { type: 'warning' }
  ).then(() => {
    importRecipes(file).then(res => {
      ElMessage.success(`导入完成：新增 ${res.addedRecipes} 道菜谱，${res.addedIngredients} 个食材`)
      loadData()
    })
  }).catch(() => {})
  return false
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.icon-blue { background: linear-gradient(135deg, #409eff, #66b1ff); }
.icon-green { background: linear-gradient(135deg, #67c23a, #85ce61); }
.icon-orange { background: linear-gradient(135deg, #e6a23c, #ebb563); }
.icon-purple { background: linear-gradient(135deg, #a058eb, #c58af9); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  font-weight: 600;
  font-size: 15px;
}

.pub-trend {
  text-align: center;
  padding: 20px 0;
}

.trend-value .number {
  font-size: 48px;
  font-weight: bold;
  color: #409eff;
}

.trend-value .unit {
  font-size: 16px;
  color: #909399;
  margin-left: 4px;
}

.trend-label {
  color: #606266;
  margin-top: 8px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
</style>
