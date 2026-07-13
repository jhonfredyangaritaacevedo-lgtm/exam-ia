import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export interface QuestionType {
  type: string
  quantity: number
}

export interface ExamRequest {
  title?: string
  area: string
  grado: string
  prompt?: string
  num_questions: number
  question_types: QuestionType[]
  files_uuid?: string
}

export interface Exam {
  id: string
  title: string
  area: string
  grado: string
  num_questions: number
  status: 'pending' | 'processing' | 'successful' | 'failed'
  result?: any
  files_uuid?: string
  created_at: string
}

export const useExamStore = defineStore('exam', () => {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  
  const exams = ref<Exam[]>([])
  const currentExam = ref<Exam | null>(null)
  const loading = ref(false)

  async function fetchExams() {
    loading.value = true
    try {
      const data = await $fetch<Exam[]>(`${config.public.apiBase}/exams`, {
        headers: { Authorization: `Bearer ${auth.accessToken}` }
      })
      exams.value = data
    } finally {
      loading.value = false
    }
  }

  async function uploadFiles(files: File[]) {
    // 1. Ask the backend for presigned PUT URLs (tiny request, no size limit)
    const { files_uuid, files: presigned } = await $fetch<{
      files_uuid: string
      files: { filename: string; key: string; url: string }[]
    }>(`${config.public.apiBase}/generate/presign`, {
      method: 'POST',
      body: { filenames: files.map(f => f.name) },
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })

    // 2. Upload each file directly to R2 (bypasses API Gateway/Lambda 6MB limit)
    await Promise.all(
      presigned.map(p => {
        const file = files.find(f => f.name === p.filename)!
        return $fetch(p.url, {
          method: 'PUT',
          body: file,
          headers: { 'Content-Type': file.type || 'application/octet-stream' }
        })
      })
    )

    return { files_uuid, files: files.map(f => f.name) }
  }

  async function generate(request: ExamRequest) {
    const data = await $fetch<Exam>(`${config.public.apiBase}/generate/exam`, {
      method: 'POST',
      body: request,
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })
    exams.value.unshift(data)
    return data
  }

  async function getStatus(id: string) {
    return await $fetch<{status: string}>(`${config.public.apiBase}/exams/${id}/status`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })
  }

  async function getExam(id: string) {
    return await $fetch<Exam>(`${config.public.apiBase}/exams/${id}`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })
  }

  async function deleteExam(id: string) {
    await $fetch(`${config.public.apiBase}/exams/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${auth.accessToken}` }
    })
    exams.value = exams.value.filter(e => e.id !== id)
    if (currentExam.value?.id === id) currentExam.value = null
  }

  return { exams, currentExam, loading, fetchExams, uploadFiles, generate, getStatus, getExam, deleteExam }
})
