<template>
  <div class="feedback-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" size="default">
        <el-form-item label="审核状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 140px"
          >
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="评分">
          <el-select
            v-model="searchForm.rating"
            placeholder="全部评分"
            clearable
            style="width: 120px"
          >
            <el-option v-for="n in 5" :key="n" :label="n + ' 星'" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="searchForm.sortBy" style="width: 120px">
            <el-option label="按时间" value="time" />
            <el-option label="按评分" value="rating" />
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
        <div class="title">评价列表</div>
      </div>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column label="评价内容" min-width="260">
          <template #default="{ row }">
            <div class="feedback-content">
              <div class="feedback-user">
                <el-avatar size="small" style="margin-right: 8px">
                  {{ row.anonymous ? '匿' : (row.userName?.charAt(0) || 'U') }}
                </el-avatar>
                <span class="user-name">
                  {{ row.anonymous ? '匿名用户' : (row.userName || '未知用户') }}
                </span>
                <el-rate
                  v-model="row.rating"
                  disabled
                  size="small"
                  style="margin-left: 10px"
                />
              </div>
              <div class="feedback-text">{{ row.content || '（无内容）' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="菜谱" width="160">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="goToRecipe(row.recipeId)"
            >
              <el-icon><View /></el-icon>
              查看菜谱
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="120" align="center">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled size="small" />
            <div style="color: #f56c6c; font-weight: bold">{{ row.rating }} 星</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="提交时间" width="180">
          <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link size="small" @click="handleApprove(row)">
                <el-icon><CircleCheck /></el-icon>
                通过
              </el-button>
              <el-button type="danger" link size="small" @click="handleReject(row)">
                <el-icon><CircleClose /></el-icon>
                拒绝
              </el-button>
            </template>
            <el-button type="primary" link size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              详情
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

    <el-dialog v-model="detailVisible" title="评价详情" width="520px">
      <div v-if="currentFeedback" class="feedback-detail">
        <div class="detail-row">
          <span class="label">用户：</span>
          <span class="value">
            {{ currentFeedback.anonymous ? '匿名用户' : (currentFeedback.userName || '未知用户') }}
            <el-tag v-if="currentFeedback.anonymous" size="small" type="info" style="margin-left: 8px">匿名</el-tag>
          </span>
        </div>
        <div class="detail-row">
          <span class="label">评分：</span>
          <span class="value">
            <el-rate v-model="currentFeedback.rating" disabled />
            <span style="margin-left: 8px; color: #f56c6c; font-weight: bold">{{ currentFeedback.rating }} 星</span>
          </span>
        </div>
        <div class="detail-row">
          <span class="label">状态：</span>
          <span class="value">
            <el-tag :type="statusType(currentFeedback.status)">{{ statusText(currentFeedback.status) }}</el-tag>
          </span>
        </div>
        <div class="detail-row">
          <span class="label">菜谱ID：</span>
          <span class="value mono">{{ currentFeedback.recipeId }}</span>
        </div>
        <div class="detail-row">
          <span class="label">评价ID：</span>
          <span class="value mono">{{ currentFeedback.id }}</span>
        </div>
        <div class="detail-row">
          <span class="label">提交时间：</span>
          <span class="value">{{ formatDate(currentFeedback.createdAt) }}</span>
        </div>
        <div class="detail-row">
          <span class="label">更新时间：</span>
          <span class="value">{{ formatDate(currentFeedback.updatedAt) }}</span>
        </div>
        <div class="detail-row" style="align-items: flex-start">
          <span class="label">评价内容：</span>
          <div class="value content-text">{{ currentFeedback.content || '（无内容）' }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <template v-if="currentFeedback?.status === 'pending'">
          <el-button type="danger" @click="handleReject(currentFeedback)">拒绝</el-button>
          <el-button type="success" @click="handleApprove(currentFeedback)">通过</el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, View, CircleCheck, CircleClose, Delete
} from '@element-plus/icons-vue'
import {
  getFeedbackList, reviewFeedback, deleteFeedback
} from '@/api/feedback'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  status: 'pending',
  rating: null,
  sortBy: 'time',
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

const detailVisible = ref(false)
const currentFeedback = ref(null)

const statusText = (status) => {
  const map = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
  return map[status] || status
}

const statusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
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
      status: searchForm.status || undefined,
      rating: searchForm.rating || undefined,
      sortBy: searchForm.sortBy,
    }
    const res = await getFeedbackList(params)
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
    status: 'pending',
    rating: null,
    sortBy: 'time',
  })
  pagination.page = 1
  loadList()
}

function goToRecipe(recipeId) {
  router.push(`/recipes/${recipeId}/preview`)
}

function handleView(row) {
  currentFeedback.value = { ...row }
  detailVisible.value = true
}

function handleApprove(row) {
  ElMessageBox.confirm('确定通过这条评价吗？', '审核确认', { type: 'success' })
    .then(() => reviewFeedback(row.id, 'approved'))
    .then(() => {
      ElMessage.success('已通过')
      loadList()
      if (detailVisible.value) detailVisible.value = false
    })
    .catch(() => {})
}

function handleReject(row) {
  ElMessageBox.confirm('确定拒绝这条评价吗？', '审核确认', { type: 'warning' })
    .then(() => reviewFeedback(row.id, 'rejected'))
    .then(() => {
      ElMessage.success('已拒绝')
      loadList()
      if (detailVisible.value) detailVisible.value = false
    })
    .catch(() => {})
}

function handleDelete(row) {
  ElMessageBox.confirm(
    '确定要删除这条评价吗？删除后不可恢复。',
    '删除确认',
    { type: 'warning' }
  ).then(() => deleteFeedback(row.id))
    .then(() => {
      ElMessage.success('删除成功')
      loadList()
    })
    .catch(() => {})
}

onMounted(() => {
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

.feedback-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.feedback-user {
  display: flex;
  align-items: center;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

.feedback-text {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.feedback-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  gap: 12px;
}

.detail-row .label {
  width: 90px;
  color: #909399;
  flex-shrink: 0;
}

.detail-row .value {
  flex: 1;
  color: #303133;
}

.detail-row .value.mono {
  font-family: monospace;
  font-size: 13px;
  color: #606266;
}

.content-text {
  line-height: 1.6;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}
</style>
