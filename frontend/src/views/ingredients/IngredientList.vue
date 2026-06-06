<template>
  <div class="ingredient-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" size="default">
        <el-form-item label="食材名称">
          <el-input
            v-model="searchForm.q"
            placeholder="请输入食材名称"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.category"
            placeholder="全部分类"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="营养标签">
          <el-select
            v-model="searchForm.nutriTag"
            placeholder="全部"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="tag in nutriTags"
              :key="tag"
              :label="tag"
              :value="tag"
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
        <div class="title">食材列表</div>
        <div class="actions">
          <el-upload
            :show-file-list="false"
            accept=".csv"
            :before-upload="handleImportCsv"
            style="display: inline-block; margin-right: 10px"
          >
            <el-button type="success">
              <el-icon><Upload /></el-icon>
              CSV批量导入
            </el-button>
          </el-upload>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增食材
          </el-button>
        </div>
      </div>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="name" label="食材名称" min-width="120" />
        <el-table-column prop="category" label="分类" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="可用单位" min-width="140">
          <template #default="{ row }">
            <el-tag
              v-for="u in row.units"
              :key="u"
              size="small"
              style="margin-right: 4px"
            >
              {{ u }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="过敏原" min-width="140">
          <template #default="{ row }">
            <el-tag
              v-for="a in row.allergens"
              :key="a"
              size="small"
              type="danger"
              style="margin-right: 4px"
            >
              {{ a }}
            </el-tag>
            <span v-if="!row.allergens?.length" style="color: #c0c4cc">无</span>
          </template>
        </el-table-column>
        <el-table-column label="营养标签" min-width="140">
          <template #default="{ row }">
            <el-tag
              v-for="t in row.nutriTags"
              :key="t"
              size="small"
              type="success"
              style="margin-right: 4px"
            >
              {{ t }}
            </el-tag>
            <span v-if="!row.nutriTags?.length" style="color: #c0c4cc">无</span>
          </template>
        </el-table-column>
        <el-table-column label="每100g营养" width="240">
          <template #default="{ row }">
            <div class="nutrition-mini">
              <span>热 {{ row.nutrition?.calories || 0 }}kcal</span>
              <span>蛋 {{ row.nutrition?.protein || 0 }}g</span>
              <span>脂 {{ row.nutrition?.fat || 0 }}g</span>
              <span>碳 {{ row.nutrition?.carbs || 0 }}g</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
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

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑食材' : '新增食材'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="食材名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入食材名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="可用单位">
          <el-select
            v-model="form.units"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入单位后回车添加"
            style="width: 100%"
          >
            <el-option v-for="u in ['克', '千克', '两', '斤', '个', '勺', '毫升', '升', '把', '片']" :key="u" :label="u" :value="u" />
          </el-select>
        </el-form-item>

        <el-form-item label="过敏原标签">
          <el-select
            v-model="form.allergens"
            multiple
            placeholder="请选择过敏原"
            style="width: 100%"
          >
            <el-option v-for="a in allergens" :key="a" :label="a" :value="a" />
          </el-select>
        </el-form-item>

        <el-form-item label="营养标签">
          <el-select
            v-model="form.nutriTags"
            multiple
            placeholder="请选择营养标签"
            style="width: 100%"
          >
            <el-option v-for="t in nutriTags" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>

        <el-form-item label="营养信息">
          <div class="nutrition-form">
            <div class="nutri-field">
              <label>卡路里</label>
              <el-input-number v-model="form.nutrition.calories" :min="0" :step="1" size="small" />
              <span class="unit">kcal/100g</span>
            </div>
            <div class="nutri-field">
              <label>蛋白质</label>
              <el-input-number v-model="form.nutrition.protein" :min="0" :step="0.1" size="small" />
              <span class="unit">g/100g</span>
            </div>
            <div class="nutri-field">
              <label>脂肪</label>
              <el-input-number v-model="form.nutrition.fat" :min="0" :step="0.1" size="small" />
              <span class="unit">g/100g</span>
            </div>
            <div class="nutri-field">
              <label>碳水</label>
              <el-input-number v-model="form.nutrition.carbs" :min="0" :step="0.1" size="small" />
              <span class="unit">g/100g</span>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, Plus, Upload, Edit, Delete
} from '@element-plus/icons-vue'
import {
  getIngredientList, createIngredient, updateIngredient,
  deleteIngredient, importIngredientsCsv
} from '@/api/ingredient'
import { getConstants } from '@/api/common'

const loading = ref(false)
const tableData = ref([])
const categories = ref([])
const allergens = ref([])
const nutriTags = ref([])

const searchForm = reactive({
  q: '',
  category: '',
  nutriTag: '',
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  name: '',
  category: '',
  units: [],
  allergens: [],
  nutriTags: [],
  nutrition: {
    calories: 0,
    protein: 0,
    fat: 0,
    carbs: 0,
  },
})

const rules = {
  name: [{ required: true, message: '请输入食材名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

const formatDate = (iso) => {
  if (!iso) return ''
  return iso.replace('T', ' ').replace('Z', '').substring(0, 19)
}

async function loadList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      q: searchForm.q || undefined,
      category: searchForm.category || undefined,
    }
    const res = await getIngredientList(params)
    let list = res.list
    if (searchForm.nutriTag) {
      list = list.filter(i => (i.nutriTags || []).includes(searchForm.nutriTag))
    }
    tableData.value = list
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
  Object.assign(searchForm, { q: '', category: '', nutriTag: '' })
  pagination.page = 1
  loadList()
}

function handleCreate() {
  isEdit.value = false
  editingId.value = ''
  Object.assign(form, {
    name: '',
    category: categories.value[0] || '',
    units: ['克'],
    allergens: [],
    nutriTags: [],
    nutrition: { calories: 0, protein: 0, fat: 0, carbs: 0 },
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    category: row.category,
    units: [...(row.units || [])],
    allergens: [...(row.allergens || [])],
    nutriTags: [...(row.nutriTags || [])],
    nutrition: {
      calories: row.nutrition?.calories || 0,
      protein: row.nutrition?.protein || 0,
      fat: row.nutrition?.fat || 0,
      carbs: row.nutrition?.carbs || 0,
    },
  })
  dialogVisible.value = true
}

function handleDialogClose() {
  if (formRef.value) formRef.value.clearValidate()
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch (e) {
    ElMessage.warning('请填写必填项')
    return
  }

  submitting.value = true
  try {
    const data = {
      name: form.name,
      category: form.category,
      units: form.units,
      allergens: form.allergens,
      nutriTags: form.nutriTags,
      nutrition: { ...form.nutrition },
    }
    if (isEdit.value) {
      await updateIngredient(editingId.value, data)
      ElMessage.success('修改成功')
    } else {
      await createIngredient(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    submitting.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(
    `确定要删除食材「${row.name}」吗？`,
    '确认删除',
    { type: 'warning' }
  ).then(() => deleteIngredient(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadList()
    })
    .catch(() => {})
}

function handleImportCsv(file) {
  ElMessageBox.confirm(
    'CSV格式说明：表头支持 name/分类、category/分类、units/单位(多个用/分隔)、allergens/过敏原(多个用/分隔)、calories/卡路里、protein/蛋白质、fat/脂肪、carbs/碳水、nutri_tags/营养标签(多个用/分隔)',
    'CSV导入说明',
    {
      confirmButtonText: '我知道了，选择文件',
      cancelButtonText: '取消',
      type: 'info',
    }
  ).then(() => {
    return importIngredientsCsv(file)
  }).then(res => {
    ElMessage.success(`导入完成：新增 ${res.added} 个，跳过 ${res.skipped} 个，错误 ${res.errors.length} 个`)
    if (res.errors.length) {
      console.warn('导入错误:', res.errors)
    }
    loadList()
  }).catch(() => {})
  return false
}

onMounted(async () => {
  try {
    const constants = await getConstants()
    categories.value = constants.ingredientCategories
    allergens.value = constants.allergens
    nutriTags.value = constants.nutriTags
  } catch (e) {}
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

.nutrition-mini {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  color: #606266;
}

.nutrition-form {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.nutri-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nutri-field label {
  width: 50px;
  color: #606266;
  font-size: 13px;
}

.nutri-field .unit {
  font-size: 12px;
  color: #909399;
}
</style>
