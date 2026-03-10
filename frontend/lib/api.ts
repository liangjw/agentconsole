import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
})

// Agent APIs
export const getAgents = () => api.get('/api/agents')
export const getAgent = (id: string) => api.get(`/api/agents/${id}`)
export const createAgent = (data: any) => api.post('/api/agents', data)
export const updateAgent = (id: string, data: any) => api.put(`/api/agents/${id}`, data)
export const deleteAgent = (id: string) => api.delete(`/api/agents/${id}`)

// Conversation APIs
export const createConversation = (agentId: string) =>
  api.post('/api/conversations', { agent_id: agentId })
export const getConversation = (id: string) => api.get(`/api/conversations/${id}`)
export const getMessages = (conversationId: string) =>
  api.get(`/api/conversations/${conversationId}/messages`)
export const sendMessage = (conversationId: string, content: string) =>
  api.post(`/api/conversations/${conversationId}/messages`, { content })
export const endConversation = (id: string) => api.delete(`/api/conversations/${id}`)
export const getSandboxFiles = (conversationId: string) =>
  api.get(`/api/conversations/${conversationId}/files`)

// Skills APIs
export const getSkills = () => api.get('/api/skills')

// Template APIs
export const getTemplates = () => api.get('/api/templates')
export const getTemplate = (id: string) => api.get(`/api/templates/${id}`)
export const getTemplateCategories = () => api.get('/api/templates/categories')
