import request from '@/utils/request'

export function getRecipeList(params) {
  return request.get('/recipes', { params })
}

export function getRecipeDetail(id) {
  return request.get(`/recipes/${id}`)
}

export function createRecipe(data) {
  return request.post('/recipes', data)
}

export function updateRecipe(id, data) {
  return request.put(`/recipes/${id}`, data)
}

export function deleteRecipe(id) {
  return request.delete(`/recipes/${id}`)
}

export function publishRecipe(id) {
  return request.post(`/recipes/${id}/publish`)
}

export function archiveRecipe(id, reason) {
  return request.post(`/recipes/${id}/archive`, { reason })
}

export function getRecipeNutrition(id) {
  return request.get(`/recipes/${id}/nutrition`)
}

export function getRecipeFeedback(id, params) {
  return request.get(`/recipes/${id}/feedback`, { params })
}

export function addDifficultyAssessment(id, data) {
  return request.post(`/recipes/${id}/difficulty-assess`, data)
}

export function exportRecipes() {
  return request.post('/recipes/export')
}

export function importRecipes(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/recipes/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
