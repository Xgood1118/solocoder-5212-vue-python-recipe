import request from '@/utils/request'

export function getIngredientList(params) {
  return request.get('/ingredients', { params })
}

export function searchIngredients(q, limit = 20) {
  return request.get('/ingredients/search', { params: { q, limit } })
}

export function getIngredientDetail(id) {
  return request.get(`/ingredients/${id}`)
}

export function createIngredient(data) {
  return request.post('/ingredients', data)
}

export function updateIngredient(id, data) {
  return request.put(`/ingredients/${id}`, data)
}

export function deleteIngredient(id) {
  return request.delete(`/ingredients/${id}`)
}

export function importIngredientsCsv(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/ingredients/import/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
