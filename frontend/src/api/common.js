import request from '@/utils/request'

export function getConstants() {
  return request.get('/constants')
}

export function getOverviewStats() {
  return request.get('/stats/overview')
}

export function getIngredientRank(limit = 20) {
  return request.get('/stats/ingredient-rank', { params: { limit } })
}
