import request from '@/utils/request'

export function getFeedbackList(params) {
  return request.get('/feedback', { params })
}

export function getFeedbackDetail(id) {
  return request.get(`/feedback/${id}`)
}

export function createFeedback(data) {
  return request.post('/feedback', data)
}

export function updateFeedback(id, data) {
  return request.patch(`/feedback/${id}`, data)
}

export function reviewFeedback(id, status) {
  return request.post(`/feedback/${id}/review`, { status })
}

export function deleteFeedback(id) {
  return request.delete(`/feedback/${id}`)
}
