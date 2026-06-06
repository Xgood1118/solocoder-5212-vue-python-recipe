<template>
  <div class="recipe-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" size="default">
        <el-form-item label="菜名">
          <el-input
            v-model="searchForm.q"
            placeholder="请输入菜名"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="菜系">
          <el-select
            v-model="searchForm.cuisine"
            placeholder="全部菜系"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="item in cuisineList"
              :key="item.name"
              :label="item.icon + ' ' + item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select
            v-model="searchForm.difficulty"
            placeholder="全部难度"
            clearable
            style="width: 120px"
          >
            <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已下架" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="烹饪时长">
          <el-select
            v-model="searchForm.timeRange"
            placeholder="不限"
            clearable
            style="width: 140px"
          >
            <el-option label="30分钟以内" value="30" />
            <el-option label="60分钟以内" value="60" />
            <el-option label="90分钟以内" value="90" />
          </el-select>
        </el-form-item>
        <el-form-item label="食材">
          <el-select
            v-model="searchForm.ingredients"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="输入食材搜索"
            :remote-method="remoteIngredientSearch"
            style="width: 240px"
          >
            <el-option
              v-for="ing in ingredientOptions"
              :key="ing.id"
              :label="ing.name"
              :value="ing.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排除过敏原">
          <el-select
            v-model="searchForm.excludeAllergens"
            multiple
            placeholder="选择过敏原"
            style="width: 200px"
          >
            <el-option
              v-for="a in allergens"
              :key="a"
              :label="a"
              :value="a"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <div class="table-header">
        <div class="title">菜谱列表</div>
        <div class="actions">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建菜谱
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出JSON
          </el-button>
        </div>
      </div>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="name" label="菜名" min-width="140">
          <template #default="{ row }">
            <div class="recipe-name-cell">
              <el-image
                v-if="row.imageUrl"
                :src="row.imageUrl"
                fit="cover"
                style="width: 48px; height: 48px; border-radius: 6px; margin-right: 10px"
              />
              <div>
                <div class="name-text">{{ row.name }}</div>
                <div class="meta-text">
                  {{ getCuisineIcon(row.cuisine) }} {{ row.cuisine }} · {{ row.difficulty }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="cookTime" label="时长" width="90" align="center">
          <template #default="{ row }">{{ row.cookTime }} 分钟</template>
        </el-table-column>
        <el-table-column prop="servings" label="人数" width="80" align="center" />
        <el-table-column label="主料数" width="80" align="center">
          <template #default="{ row }">{{ row.mainIngredients?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="下架原因" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.archived">{{ row.archived.reason }}</span>
            <span v-else style="color: #c0c4cc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handlePreview(row)">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'draft' || row.status === 'archived'"
              type="success"
              link
              size="small"
              @click="handlePublish(row)"
            >
              <el-icon><Promotion /></el-icon>
              发布
            </el-button>
            <el-button
              v-if="row.status === 'published'"
              type="warning"
              link
              size="small"
              @click="handleArchive(row)"
            >
              <el-icon><Delete /></el-icon>
              下架
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @size-change="loadList"
        @current-change="loadList"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, Plus, Download, View, Edit, Delete, Promotion
} from '@element-plus/icons-vue'
import {
  getRecipeList, deleteRecipe, publishRecipe, archiveRecipe, exportRecipes
} from '@/api/recipe'
import { searchIngredients } from '@/api/ingredient'
import { getConstants as getSysConstants } from '@/api/common'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const ingredientOptions = ref([])
const cuisineList = ref([])
const difficulties = ref([])
const allergens = ref([])
const archiveReasons = ref([])

const searchForm = reactive({
  q: '',
  cuisine: '',
  difficulty: '',
  status: '',
  timeRange: '',
  ingredients: [],
  excludeAllergens: [],
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

const statusText = (status) => {
  const map = { draft: '草稿', published: '已发布', archived: '已下架' }
  return map[status] || status
}

const statusType = (status) => {
  const map = { draft: 'info', published: 'success', archived: 'danger' }
  return map[status] || 'info'
}

const getCuisineIcon = (name) => {
  const item = cuisineList.value.find(c => c.name === name)
  return item?.icon || '🍽️'
}

const formatDate = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').replace('Z', '').substring(0, 19)
}

let searchTimer = null
function remoteIngredientSearch(query) {
  if (searchTimer) clearTimeout(searchTimer)
  if (!query) {
    ingredientOptions.value = []
    return
  }
  searchTimer = setTimeout(async () => {
    try {
      ingredientOptions.value = await searchIngredients(query, 20)
    } catch (e) {}
  }, 300)
}

async function loadList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      q: searchForm.q || undefined,
      cuisine: searchForm.cuisine || undefined,
      difficulty: searchForm.difficulty || undefined,
      status: searchForm.status || undefined,
      maxTime: searchForm.timeRange ? Number(searchForm.timeRange) : undefined,
      ingredients: searchForm.ingredients?.length ? searchForm.ingredients : undefined,
      excludeAllergens: searchForm.excludeAllergens?.length ? searchForm.excludeAllergens : undefined,
    }
    const res = await getRecipeList(params)
    tableData.value = res.list
    pagination.total = res.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadList()
}

function handleReset() {
  Object.assign(searchForm, {
    q: '',
    cuisine: '',
    difficulty: '',
    status: '',
    timeRange: '',
    ingredients: [],
    excludeAllergens: [],
  })
  pagination.page = 1
  loadList()
}

function handleCreate() {
  router.push('/recipes/new')
}

function handleEdit(row) {
  if (row.status === 'published') {
    ElMessage.warning('已发布的菜谱不能直接编辑，请先下架')
    return
  }
  router.push(`/recipes/${row.id}/edit`)
}

function handlePreview(row) {
  router.push(`/recipes/${row.id}/preview`)
}

function handlePublish(row) {
  ElMessageBox.confirm(`确定要发布菜谱「${row.name}」吗？`, '确认发布', { type: 'warning' })
    .then(() => publishRecipe(row.id))
    .then(() => {
      ElMessage.success('发布成功')
      loadList()
    })
    .catch(() => {})
}

function handleArchive(row) {
  ElMessageBox.prompt('请选择下架原因', '下架确认', {
    confirmButtonText: '确定下架',
    cancelButtonText: '取消',
    inputType: 'select',
    inputValue: archiveReasons.value[0],
    inputOptions: archiveReasons.value.map(r => ({ value: r, label: r })),
    type: 'warning',
  }).then(({ value }) => {
    return archiveRecipe(row.id, value)
  }).then(() => {
    ElMessage.success('已下架')
    loadList()
  }).catch(() => {})
}

function handleDelete(row) {
  ElMessageBox.prompt(
    `请输入菜名「${row.name}」确认删除`,
    '二次确认删除',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      inputPattern: new RegExp(`^${row.name}$`),
      inputErrorMessage: '菜名输入不正确',
    }
  ).then(() => {
    return ElMessageBox.confirm('此操作不可恢复，真的要删除吗？', '再次确认', { type: 'error' })
  }).then(() => deleteRecipe(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadList()
    })
    .catch(() => {})
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

onMounted(async () => {
  try {
    const constants = await getSysConstants()
    cuisineList.value = constants.cuisines
    difficulties.value = constants.difficulties
    allergens.value = constants.allergens
    archiveReasons.value = constants.archiveReasons
  } catch (e) {
    console.error(e)
  }
  loadList()
})
</script>

<style scoped>
.search-card {
  border-radius: 6px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.recipe-name-cell {
  display: flex;
  align-items: center;
}

.name-text {
  font-weight: 500;
  color: #303133;
}

.meta-text {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
