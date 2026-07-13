<template>
  <div class="min-h-full px-4 pt-5 pb-8 max-w-3xl mx-auto">

    <div class="mb-6">
      <h1 class="text-xl font-bold text-gray-900">Administración del RAG</h1>
      <p class="text-sm text-gray-500 mt-1">Gestiona los documentos de referencia que usa la IA para generar exámenes</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 gap-3 mb-6">
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Documentos</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.documents }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Chunks indexados</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.chunks }}</p>
      </div>
    </div>

    <!-- Upload -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 mb-4">
      <p class="text-sm font-semibold text-gray-700 mb-3">Subir documentos</p>
      <div
        class="border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer"
        :class="isDragging ? 'border-sky-400 bg-sky-50' : 'border-gray-200 hover:border-sky-300 hover:bg-gray-50'"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
        @click="fileInputRef?.click()"
      >
        <input ref="fileInputRef" type="file" multiple accept=".pdf,.docx,.pptx,.xlsx" class="hidden" @change="onFileSelect" />
        <span class="icon-[ic--twotone-upload-file] w-10 h-10 text-gray-300 block mx-auto mb-2"></span>
        <p class="text-sm font-medium text-gray-600">Arrastra o haz clic para seleccionar</p>
        <p class="text-xs text-gray-400 mt-1">PDF, Word, PowerPoint, Excel · Puedes seleccionar varios</p>
      </div>

      <div v-if="pendingFiles.length" class="mt-3 space-y-1.5">
        <div
          v-for="(file, i) in pendingFiles"
          :key="i"
          class="flex items-center justify-between bg-sky-50 border border-sky-200 rounded-lg px-3 py-2"
        >
          <div class="flex items-center gap-2 text-sm text-sky-700 min-w-0">
            <span class="icon-[ic--twotone-description] w-4 h-4 shrink-0"></span>
            <span class="truncate">{{ file.name }}</span>
          </div>
          <Button icon="pi pi-times" text rounded size="small" severity="secondary" class="shrink-0 ml-2" @click="pendingFiles.splice(i, 1)" />
        </div>
        <div class="flex justify-end gap-2 pt-1">
          <Button label="Limpiar" text size="small" severity="secondary" @click="pendingFiles = []" />
          <Button
            :label="`Subir ${pendingFiles.length} archivo${pendingFiles.length > 1 ? 's' : ''}`"
            icon="pi pi-upload"
            size="small"
            :loading="uploading"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
            @click="uploadFiles"
          />
        </div>
      </div>
    </div>

    <!-- Documentos -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm mb-4">
      <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <p class="text-sm font-semibold text-gray-700">Documentos en el índice</p>
        <Button
          icon="pi pi-refresh"
          text rounded size="small"
          class="text-gray-400"
          :loading="loadingDocs"
          @click="loadDocuments"
        />
      </div>

      <div v-if="documents.length === 0" class="text-center py-10">
        <i class="pi pi-inbox text-3xl text-gray-200 block mb-2"></i>
        <p class="text-sm text-gray-400">Sin documentos subidos</p>
      </div>

      <div
        v-for="doc in documents"
        :key="doc.id"
        class="group flex items-center justify-between px-4 py-3 border-b border-gray-50 last:border-0"
      >
        <div class="flex items-center gap-3 min-w-0">
          <span class="icon-[ic--twotone-description] w-5 h-5 text-sky-500 shrink-0"></span>
          <div class="min-w-0">
            <p class="text-sm font-medium text-gray-800 truncate">{{ doc.filename }}</p>
            <p class="text-xs text-gray-400">{{ formatDate(doc.created_at) }}</p>
          </div>
        </div>
        <div
          class="flex items-center gap-1 shrink-0 transition-opacity"
          :class="reindexingDocId === doc.id && reindexStatus.running ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'"
        >
          <Button
            v-tooltip.top="'Re-indexar'"
            icon="pi pi-sync"
            text rounded size="small" severity="secondary"
            :loading="reindexingDocId === doc.id && reindexStatus.running"
            :disabled="reindexStatus.running && reindexingDocId !== doc.id"
            @click="triggerReindexSingle(doc)"
          />
          <Button
            icon="pi pi-download"
            text rounded size="small" severity="secondary"
            :disabled="reindexStatus.running"
            @click="downloadDocument(doc)"
          />
          <Button
            icon="pi pi-trash"
            text rounded size="small" severity="danger"
            :disabled="reindexStatus.running"
            @click="confirmDelete(doc)"
          />
        </div>
      </div>
    </div>

    <!-- Re-indexar -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-semibold text-gray-700">Re-indexar RAG</p>
          <p class="text-xs text-gray-500 mt-0.5">Procesa todos los documentos y regenera los embeddings en la base de datos vectorial</p>
        </div>
        <Button
          label="Regenerar"
          icon="pi pi-bolt"
          :loading="reindexStatus.running"
          :disabled="documents.length === 0"
          style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
          @click="triggerReindex"
        />
      </div>

      <div v-if="reindexStatus.progress && reindexStatus.progress !== 'Sin ejecutar'" class="mt-3 flex items-center gap-2">
        <i v-if="reindexStatus.running" class="pi pi-spin pi-spinner text-sky-500 text-sm"></i>
        <i v-else-if="reindexStatus.error" class="pi pi-times-circle text-red-500 text-sm"></i>
        <i v-else class="pi pi-check-circle text-green-500 text-sm"></i>
        <p class="text-xs" :class="reindexStatus.error ? 'text-red-600' : 'text-gray-600'">
          {{ reindexStatus.error || reindexStatus.progress }}
        </p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

const auth = useAuthStore()
const config = useRuntimeConfig()
const confirm = useConfirm()
const toast = useToast()

if (auth.user?.role !== 'admin') {
  navigateTo('/')
}

interface RagDoc {
  id: string
  filename: string
  s3_key: string
  status: string
  created_at: string
}

const stats = ref({ documents: 0, chunks: 0 })
const documents = ref<RagDoc[]>([])
const loadingDocs = ref(false)
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const pendingFiles = ref<File[]>([])
const uploading = ref(false)
const reindexStatus = ref({ running: false, progress: 'Sin ejecutar', error: null as string | null })
const reindexingDocId = ref<string | null>(null)

let pollInterval: ReturnType<typeof setInterval> | null = null

const headers = computed(() => ({ Authorization: `Bearer ${auth.accessToken}` }))

async function loadStats() {
  const data = await $fetch<{ documents: number; chunks: number }>(
    `${config.public.apiBase}/admin/rag/stats`,
    { headers: headers.value }
  )
  stats.value = data
}

async function loadDocuments() {
  loadingDocs.value = true
  try {
    documents.value = await $fetch<RagDoc[]>(
      `${config.public.apiBase}/admin/rag/documents`,
      { headers: headers.value }
    )
  } finally {
    loadingDocs.value = false
  }
}

async function loadReindexStatus() {
  const data = await $fetch<typeof reindexStatus.value>(
    `${config.public.apiBase}/admin/rag/reindex/status`,
    { headers: headers.value }
  )
  reindexStatus.value = data
  if (!data.running && pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
    reindexingDocId.value = null
    await loadStats()
  }
}

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) pendingFiles.value.push(...Array.from(input.files))
  input.value = ''
}

const onDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files) pendingFiles.value.push(...Array.from(e.dataTransfer.files))
}

async function uploadFiles() {
  if (!pendingFiles.value.length) return
  uploading.value = true
  let ok = 0
  let fail = 0
  try {
    for (const file of pendingFiles.value) {
      try {
        const form = new FormData()
        form.append('file', file)
        await $fetch(`${config.public.apiBase}/admin/rag/upload`, {
          method: 'POST',
          body: form,
          headers: headers.value,
        })
        ok++
      } catch {
        fail++
      }
    }
    if (ok) toast.add({ severity: 'success', summary: 'Subidos', detail: `${ok} archivo${ok > 1 ? 's' : ''} subido${ok > 1 ? 's' : ''}`, life: 3000 })
    if (fail) toast.add({ severity: 'error', summary: 'Error', detail: `${fail} archivo${fail > 1 ? 's' : ''} no se pudo${fail > 1 ? 'ieron' : ''} subir`, life: 4000 })
    pendingFiles.value = []
    await Promise.all([loadDocuments(), loadStats()])
  } finally {
    uploading.value = false
  }
}

async function downloadDocument(doc: RagDoc) {
  const blob = await $fetch<Blob>(`${config.public.apiBase}/admin/rag/documents/${doc.id}/download`, {
    headers: headers.value,
    responseType: 'blob',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = doc.filename
  a.click()
  URL.revokeObjectURL(url)
}

function confirmDelete(doc: RagDoc) {
  confirm.require({
    message: `¿Eliminar "${doc.filename}"?`,
    header: 'Confirmar',
    icon: 'pi pi-trash',
    rejectLabel: 'Cancelar',
    acceptLabel: 'Eliminar',
    acceptClass: 'p-button-danger',
    accept: () => deleteDocument(doc.id),
  })
}

async function deleteDocument(id: string) {
  try {
    await $fetch(`${config.public.apiBase}/admin/rag/documents/${id}`, {
      method: 'DELETE',
      headers: headers.value,
    })
    documents.value = documents.value.filter(d => d.id !== id)
    await loadStats()
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar', life: 4000 })
  }
}

async function triggerReindex() {
  try {
    await $fetch(`${config.public.apiBase}/admin/rag/reindex`, {
      method: 'POST',
      headers: headers.value,
    })
    reindexStatus.value = { running: true, progress: 'Iniciando...', error: null }
    pollInterval = setInterval(loadReindexStatus, 3000)
  } catch (err: any) {
    toast.add({ severity: 'warn', summary: 'Aviso', detail: err?.data?.detail ?? 'Error al iniciar', life: 4000 })
  }
}

async function triggerReindexSingle(doc: RagDoc) {
  try {
    await $fetch(`${config.public.apiBase}/admin/rag/documents/${doc.id}/reindex`, {
      method: 'POST',
      headers: headers.value,
    })
    reindexingDocId.value = doc.id
    reindexStatus.value = { running: true, progress: 'Iniciando...', error: null }
    pollInterval = setInterval(loadReindexStatus, 3000)
  } catch (err: any) {
    toast.add({ severity: 'warn', summary: 'Aviso', detail: err?.data?.detail ?? 'Error al iniciar', life: 4000 })
  }
}

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })

onMounted(async () => {
  await Promise.all([loadStats(), loadDocuments(), loadReindexStatus()])
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>
