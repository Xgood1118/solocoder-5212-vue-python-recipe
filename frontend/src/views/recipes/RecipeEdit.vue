<template>
  <div class="recipe-edit">
    <el-page-header @back="$router.back()" :content="isEdit ? '编辑菜谱' : '新建菜谱'">
      <template #extra>
        <el-button @click="$router.back()">取消</el-button>
        <el-button @click="handlePreview" :disabled="!canPreview">
          <el-icon><View /></el-icon>
          预览
        </el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-page-header>

    <el-card shadow="never" style="margin-top: 16px">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
      >
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="菜名" prop="name">
                <el-input v-model="form.name" placeholder="请输入菜名" maxlength="50" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="菜系" prop="cuisine">
                <el-select v-model="form.cuisine" placeholder="请选择菜系" style="width: 100%">
                  <el-option
                    v-for="item in cuisineList"
                    :key="item.name"
                    :label="item.icon + ' ' + item.name"
                    :value="item.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="难度" prop="difficulty">
                <el-radio-group v-model="form.difficulty">
                  <el-radio-button v-for="d in difficulties" :key="d" :value="d">{{ d }}</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="烹饪时长" prop="cookTime">
                <el-input-number v-model="form.cookTime" :min="1" :max="600" style="width: 100%" />
                <span style="margin-left: 8px; color: #909399; font-size: 13px">分钟</span>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="适合人数" prop="servings">
                <el-input-number v-model="form.servings" :min="1" :max="20" style="width: 100%" />
                <span style="margin-left: 8px; color: #909399; font-size: 13px">人份</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="封面图片" prop="imageUrl">
                <el-input v-model="form.imageUrl" placeholder="请输入图片URL" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-title">
            主料
            <el-button type="primary" link size="small" @click="addIngredient('mainIngredients')">
              <el-icon><Plus /></el-icon>添加
            </el-button>
          </div>
          <div class="ingredient-list" v-if="form.mainIngredients.length">
            <div
              v-for="(ing, idx) in form.mainIngredients"
              :key="idx"
              class="ingredient-row"
            >
              <span class="drag-handle">⋮⋮</span>
              <el-select
                v-model="ing.name"
                filterable
                remote
                reserve-keyword
                placeholder="搜索食材"
                :remote-method="(q) => remoteSearch(q, 'mainIngredients', idx)"
                style="width: 180px"
                @change="(val) => onIngredientSelect(val, 'mainIngredients', idx)"
              >
                <el-option
                  v-for="opt in mainIngOptions[idx] || []"
                  :key="opt.id"
                  :label="opt.name"
                  :value="opt.name"
                />
              </el-select>
              <el-input-number v-model="ing.amount" :min="0" :step="0.5" style="width: 100px; margin: 0 8px" />
              <el-select v-model="ing.unit" placeholder="单位" style="width: 80px; margin-right: 8px">
                <el-option v-for="u in getIngredientUnits(ing.name)" :key="u" :label="u" :value="u" />
              </el-select>
              <el-checkbox v-model="ing.optional" style="margin-right: 10px">可选</el-checkbox>
              <el-button type="danger" link @click="removeIngredient('mainIngredients', idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <el-empty v-else description="暂无主料" :image-size="60" />
        </div>

        <div class="form-section">
          <div class="section-title">
            辅料
            <el-button type="primary" link size="small" @click="addIngredient('auxIngredients')">
              <el-icon><Plus /></el-icon>添加
            </el-button>
          </div>
          <div class="ingredient-list" v-if="form.auxIngredients.length">
            <div
              v-for="(ing, idx) in form.auxIngredients"
              :key="idx"
              class="ingredient-row"
            >
              <span class="drag-handle">⋮⋮</span>
              <el-select
                v-model="ing.name"
                filterable
                remote
                reserve-keyword
                placeholder="搜索食材"
                :remote-method="(q) => remoteSearch(q, 'auxIngredients', idx)"
                style="width: 180px"
                @change="(val) => onIngredientSelect(val, 'auxIngredients', idx)"
              >
                <el-option
                  v-for="opt in auxIngOptions[idx] || []"
                  :key="opt.id"
                  :label="opt.name"
                  :value="opt.name"
                />
              </el-select>
              <el-input-number v-model="ing.amount" :min="0" :step="0.5" style="width: 100px; margin: 0 8px" />
              <el-select v-model="ing.unit" placeholder="单位" style="width: 80px; margin-right: 8px">
                <el-option v-for="u in getIngredientUnits(ing.name)" :key="u" :label="u" :value="u" />
              </el-select>
              <el-checkbox v-model="ing.optional" style="margin-right: 10px">可选</el-checkbox>
              <el-button type="danger" link @click="removeIngredient('auxIngredients', idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <el-empty v-else description="暂无辅料" :image-size="60" />
        </div>

        <div class="form-section">
          <div class="section-title">
            调料
            <el-button type="primary" link size="small" @click="addIngredient('seasonings')">
              <el-icon><Plus /></el-icon>添加
            </el-button>
          </div>
          <div class="ingredient-list" v-if="form.seasonings.length">
            <div
              v-for="(ing, idx) in form.seasonings"
              :key="idx"
              class="ingredient-row"
            >
              <span class="drag-handle">⋮⋮</span>
              <el-select
                v-model="ing.name"
                filterable
                remote
                reserve-keyword
                placeholder="搜索食材"
                :remote-method="(q) => remoteSearch(q, 'seasonings', idx)"
                style="width: 180px"
                @change="(val) => onIngredientSelect(val, 'seasonings', idx)"
              >
                <el-option
                  v-for="opt in seasoningOptions[idx] || []"
                  :key="opt.id"
                  :label="opt.name"
                  :value="opt.name"
                />
              </el-select>
              <el-input-number v-model="ing.amount" :min="0" :step="0.5" style="width: 100px; margin: 0 8px" />
              <el-select v-model="ing.unit" placeholder="单位" style="width: 80px; margin-right: 8px">
                <el-option v-for="u in getIngredientUnits(ing.name)" :key="u" :label="u" :value="u" />
              </el-select>
              <el-checkbox v-model="ing.optional" style="margin-right: 10px">可选</el-checkbox>
              <el-button type="danger" link @click="removeIngredient('seasonings', idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <el-empty v-else description="暂无调料" :image-size="60" />
        </div>

        <div class="form-section">
          <div class="section-title">
            烹饪步骤
            <el-button type="primary" link size="small" @click="addStep">
              <el-icon><Plus /></el-icon>添加步骤
            </el-button>
            <span style="color: #909399; font-size: 13px; margin-left: 10px">拖拽调整顺序</span>
          </div>
          <div ref="stepsListRef" class="steps-list">
            <div
              v-for="(step, idx) in form.steps"
              :key="idx"
              class="step-row"
              :data-index="idx"
            >
              <div class="step-header">
                <span class="step-order">
                  <el-icon style="cursor: move"><Rank /></el-icon>
                  第 {{ idx + 1 }} 步
                </span>
                <el-button type="danger" link size="small" @click="removeStep(idx)">
                  <el-icon><Delete /></el-icon>删除
                </el-button>
              </div>
              <div class="step-body">
                <el-form-item label="步骤描述" label-width="80px" style="margin-bottom: 8px">
                  <el-input
                    v-model="step.description"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入步骤描述"
                    maxlength="500"
                    show-word-limit
                  />
                </el-form-item>
                <el-row :gutter="16">
                  <el-col :span="8">
                    <el-form-item label="预计时长" label-width="80px" style="margin-bottom: 8px">
                      <el-input-number v-model="step.duration" :min="0" :max="120" />
                      <span style="margin-left: 6px; color: #909399; font-size: 13px">分钟</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="16">
                    <el-form-item label="小贴士" label-width="80px" style="margin-bottom: 8px">
                      <el-input v-model="step.tip" placeholder="小贴士（可选）" maxlength="200" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <div class="step-images">
                  <span style="color: #606266; font-size: 13px">步骤图片：</span>
                  <div v-if="step.images && step.images.length" class="image-list">
                    <div v-for="(img, iIdx) in step.images" :key="iIdx" class="image-item">
                      <el-image :src="img" fit="cover" style="width: 60px; height: 60px; border-radius: 4px" />
                      <el-button
                        type="danger"
                        size="small"
                        circle
                        style="position: absolute; top: -6px; right: -6px"
                        @click="removeStepImage(idx, iIdx)"
                      >
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </div>
                  </div>
                  <el-input
                    v-model="step.newImageUrl"
                    placeholder="输入图片URL后回车添加"
                    size="small"
                    style="width: 280px; margin-left: 8px"
                    @keyup.enter="addStepImage(idx)"
                  />
                  <el-button size="small" type="primary" @click="addStepImage(idx)" style="margin-left: 6px">
                    添加
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-if="!form.steps.length" description="暂无步骤" :image-size="60" />
        </div>
      </el-form>
    </el-card>

    <div style="margin-top: 20px; text-align: right">
      <el-button @click="$router.back()">取消</el-button>
      <el-button @click="handlePreview" :disabled="!canPreview">预览</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  View, Check, Plus, Delete, Rank, Close
} from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import { getRecipeDetail, createRecipe, updateRecipe } from '@/api/recipe'
import { searchIngredients } from '@/api/ingredient'
import { getConstants } from '@/api/common'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const isEdit = computed(() => !!route.params.id)
const stepsListRef = ref(null)

const cuisineList = ref([])
const difficulties = ref([])

const ingredientCache = ref({})
const mainIngOptions = ref([])
const auxIngOptions = ref([])
const seasoningOptions = ref([])

const form = reactive({
  name: '',
  cuisine: '',
  difficulty: '简单',
  cookTime: 30,
  servings: 2,
  imageUrl: '',
  mainIngredients: [],
  auxIngredients: [],
  seasonings: [],
  steps: [],
})

const rules = {
  name: [{ required: true, message: '请输入菜名', trigger: 'blur' }],
  cuisine: [{ required: true, message: '请选择菜系', trigger: 'change' }],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }],
  cookTime: [{ required: true, message: '请输入烹饪时长', trigger: 'blur' }],
  servings: [{ required: true, message: '请输入适合人数', trigger: 'blur' }],
}

const canPreview = computed(() => {
  return form.name && form.cuisine && form.steps.length > 0
})

function addIngredient(type) {
  form[type].push({
    ingredientId: null,
    name: '',
    amount: 0,
    unit: '克',
    optional: false,
  })
}

function removeIngredient(type, idx) {
  form[type].splice(idx, 1)
}

function getIngredientUnits(name) {
  if (!name) return ['克', '个', '勺', '毫升']
  const cached = ingredientCache.value[name]
  if (cached && cached.units && cached.units.length) {
    return cached.units
  }
  return ['克', '个', '勺', '毫升']
}

let searchTimers = {}
function remoteSearch(query, type, idx) {
  const key = `${type}_${idx}`
  if (searchTimers[key]) clearTimeout(searchTimers[key])
  if (!query) {
    if (type === 'mainIngredients') mainIngOptions.value[idx] = []
    if (type === 'auxIngredients') auxIngOptions.value[idx] = []
    if (type === 'seasonings') seasoningOptions.value[idx] = []
    return
  }
  searchTimers[key] = setTimeout(async () => {
    try {
      const list = await searchIngredients(query, 15)
      list.forEach(ing => {
        ingredientCache.value[ing.name] = ing
      })
      if (type === 'mainIngredients') mainIngOptions.value[idx] = list
      if (type === 'auxIngredients') auxIngOptions.value[idx] = list
      if (type === 'seasonings') seasoningOptions.value[idx] = list
    } catch (e) {}
  }, 200)
}

function onIngredientSelect(val, type, idx) {
  const cached = ingredientCache.value[val]
  if (cached) {
    form[type][idx].ingredientId = cached.id
    if (!form[type][idx].unit && cached.units && cached.units.length) {
      form[type][idx].unit = cached.units[0]
    }
  }
}

function addStep() {
  form.steps.push({
    order: form.steps.length + 1,
    description: '',
    duration: 5,
    tip: '',
    images: [],
    newImageUrl: '',
  })
  nextTick(() => initSortable())
}

function removeStep(idx) {
  form.steps.splice(idx, 1)
  form.steps.forEach((s, i) => { s.order = i + 1 })
}

function addStepImage(idx) {
  const step = form.steps[idx]
  if (!step.newImageUrl || !step.newImageUrl.trim()) return
  step.images.push(step.newImageUrl.trim())
  step.newImageUrl = ''
}

function removeStepImage(stepIdx, imgIdx) {
  form.steps[stepIdx].images.splice(imgIdx, 1)
}

let sortable = null
function initSortable() {
  if (sortable) sortable.destroy()
  if (!stepsListRef.value) return
  sortable = new Sortable(stepsListRef.value, {
    animation: 200,
    handle: '.step-header',
    onEnd(evt) {
      const { oldIndex, newIndex } = evt
      if (oldIndex === newIndex) return
      const steps = form.steps
      const [moved] = steps.splice(oldIndex, 1)
      steps.splice(newIndex, 0, moved)
      steps.forEach((s, i) => { s.order = i + 1 })
    },
  })
}

async function handleSave() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch (e) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    const data = {
      name: form.name,
      cuisine: form.cuisine,
      difficulty: form.difficulty,
      cookTime: form.cookTime,
      servings: form.servings,
      imageUrl: form.imageUrl,
      mainIngredients: form.mainIngredients.map(({ ingredientId, name, amount, unit, optional }) =>
        ({ ingredientId, name, amount, unit, optional })
      ),
      auxIngredients: form.auxIngredients.map(({ ingredientId, name, amount, unit, optional }) =>
        ({ ingredientId, name, amount, unit, optional })
      ),
      seasonings: form.seasonings.map(({ ingredientId, name, amount, unit, optional }) =>
        ({ ingredientId, name, amount, unit, optional })
      ),
      steps: form.steps.map((s, idx) => ({
        order: idx + 1,
        description: s.description,
        duration: s.duration,
        tip: s.tip,
        images: s.images || [],
      })),
    }

    let result
    if (isEdit.value) {
      result = await updateRecipe(route.params.id, data)
      ElMessage.success('保存成功')
    } else {
      result = await createRecipe(data)
      ElMessage.success('创建成功')
    }
    router.push('/recipes')
  } finally {
    saving.value = false
  }
}

function handlePreview() {
  localStorage.setItem('recipe_preview', JSON.stringify({
    name: form.name,
    cuisine: form.cuisine,
    difficulty: form.difficulty,
    cookTime: form.cookTime,
    servings: form.servings,
    imageUrl: form.imageUrl,
    mainIngredients: form.mainIngredients,
    auxIngredients: form.auxIngredients,
    seasonings: form.seasonings,
    steps: form.steps.map(s => ({ ...s, images: s.images || [] })),
  }))
  router.push('/recipes/draft/preview')
}

async function loadDetail() {
  if (!isEdit.value) return
  try {
    const data = await getRecipeDetail(route.params.id)
    form.name = data.name
    form.cuisine = data.cuisine
    form.difficulty = data.difficulty
    form.cookTime = data.cookTime
    form.servings = data.servings
    form.imageUrl = data.imageUrl || ''
    form.mainIngredients = (data.mainIngredients || []).map(ing => ({ ...ing }))
    form.auxIngredients = (data.auxIngredients || []).map(ing => ({ ...ing }))
    form.seasonings = (data.seasonings || []).map(ing => ({ ...ing }))
    form.steps = (data.steps || []).map(s => ({
      ...s,
      newImageUrl: '',
      images: s.images || [],
    }))
    nextTick(() => initSortable())
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  try {
    const constants = await getConstants()
    cuisineList.value = constants.cuisines
    difficulties.value = constants.difficulties
    if (cuisineList.value.length) {
      form.cuisine = form.cuisine || cuisineList.value[0].name
    }
  } catch (e) {
    console.error(e)
  }

  if (isEdit.value) {
    loadDetail()
  } else {
    form.steps.push({
      order: 1,
      description: '',
      duration: 5,
      tip: '',
      images: [],
      newImageUrl: '',
    })
    nextTick(() => initSortable())
  }
})
</script>

<style scoped>
.recipe-edit {
  padding-bottom: 20px;
}

.form-section {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #ebeef5;
}

.form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.ingredient-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ingredient-row {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.drag-handle {
  cursor: move;
  color: #c0c4cc;
  margin-right: 8px;
  user-select: none;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.step-row {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f0f2f5;
  border-radius: 8px 8px 0 0;
  cursor: move;
}

.step-order {
  font-weight: 600;
  color: #409eff;
  display: flex;
  align-items: center;
  gap: 6px;
}

.step-body {
  padding: 14px 16px;
}

.step-images {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 8px;
  gap: 8px;
}

.image-list {
  display: flex;
  gap: 10px;
}

.image-item {
  position: relative;
}
</style>
