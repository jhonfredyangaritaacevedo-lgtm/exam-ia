<template>
  <div class="min-h-full flex flex-col items-center justify-start px-4 pt-5 pb-8">

    <!-- Estado: Generador -->
    <div v-if="view === 'generator'" class="w-full max-w-3xl">

      <!-- Encabezado -->
      <div class="text-center mb-4">
        <AppLogo :icon-only="true" :height="44" class="mx-auto mb-3" />
        <h1 class="text-xl font-bold text-gray-900">¿Sobre qué quieres generar un examen?</h1>
        <p class="text-sm text-gray-500 mt-1">Sube tus materiales de clase o escribe el tema, y la IA hará el resto</p>
      </div>

      <!-- Formulario -->
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">

        <!-- Título -->
        <div class="p-3 border-b border-gray-100">
          <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Título del examen</label>
          <InputText
            v-model="form.title"
            placeholder="Ej: Evaluación de Biología - Fotosíntesis"
            fluid
          />
        </div>

        <!-- Área + Grado -->
        <div class="flex gap-3 p-3 border-b border-gray-100">
          <div class="flex-1">
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Área curricular</label>
            <Select
              v-model="form.area"
              :options="areas"
              placeholder="Selecciona el área"
              fluid
            />
          </div>
          <div class="w-36">
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Grado</label>
            <Select
              v-model="form.grado"
              :options="grados"
              option-label="label"
              option-value="value"
              placeholder="Grado"
              fluid
            />
          </div>
        </div>

        <!-- Zona de archivos -->
        <div
          class="m-3 border-2 border-dashed rounded-xl p-4 text-center transition-colors cursor-pointer"
          :class="isDragging ? 'border-sky-400 bg-sky-50' : 'border-gray-200 hover:border-sky-300 hover:bg-gray-50'"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="fileInputRef?.click()"
        >
          <input ref="fileInputRef" type="file" multiple accept=".pdf,.docx,.pptx,.xlsx" class="hidden" @change="onFileSelect" />
          <div v-if="form.files.length === 0">
            <span class="icon-[ic--twotone-upload-file] w-10 h-10 text-gray-300 block mx-auto mb-2"></span>
            <p class="text-sm font-medium text-gray-600">Arrastra tus documentos aquí</p>
            <p class="text-xs text-gray-400 mt-1">PDF, Word, PowerPoint, Excel · Máx. 10 MB c/u</p>
          </div>
          <div v-else class="flex flex-wrap gap-2 justify-center">
            <div
              v-for="(file, i) in form.files"
              :key="i"
              class="flex items-center gap-1.5 bg-sky-50 border border-sky-200 rounded-lg px-2.5 py-1.5 text-xs text-sky-700"
            >
              <span class="icon-[ic--twotone-description] w-3.5 h-3.5"></span>
              {{ file.name }}
              <button class="text-sky-400 hover:text-red-500" @click.stop="removeFile(i)">
                <span class="icon-[ic--twotone-close] w-3 h-3"></span>
              </button>
            </div>
            <button class="text-xs text-sky-500 hover:underline" @click.stop="fileInputRef?.click()">+ Agregar más</button>
          </div>
        </div>

        <!-- Prompt / Instrucciones -->
        <div class="px-3 pb-3">
          <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Instrucciones adicionales (opcional)</label>
          <Textarea
            v-model="form.prompt"
            placeholder="Ej: Enfocarse en la fase luminosa de la fotosíntesis. Incluir preguntas de análisis, no solo memorización..."
            :rows="5"
            fluid
            class="resize-none"
          />
        </div>

        <!-- Distribución de preguntas -->
        <div class="px-3 pb-3 border-t border-gray-100 pt-3">
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs font-semibold text-gray-500">Distribución de preguntas</label>
            <span class="text-xs font-bold px-2 py-0.5 rounded-full bg-sky-100 text-sky-700">
              {{ totalQuestions }} preguntas en total
            </span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div v-for="qt in questionTypes" :key="qt.key">
              <label class="text-xs text-gray-500 mb-1 block">{{ qt.label }}</label>
              <InputNumber v-model="form.types[qt.key]" :min="0" :max="20" show-buttons button-layout="horizontal"
                decrement-button-icon="pi pi-minus" increment-button-icon="pi pi-plus"
                :input-style="{ width: '3rem', textAlign: 'center' }" fluid />
            </div>
          </div>
        </div>

        <!-- Footer con botón -->
        <div class="px-3 pb-3 flex justify-end">
          <Button
            label="Generar Examen"
            icon="pi pi-sparkles"
            icon-pos="right"
            size="large"
            :disabled="!form.area || !form.grado"
            @click="generateExam"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
          />
        </div>
      </div>

      <p class="text-center text-xs text-gray-400 mt-4">
        El examen se alineará automáticamente con los Estándares Básicos de Competencias del MEN (Colombia)
      </p>
    </div>

    <!-- Estado: Generando -->
    <div v-else-if="view === 'generating'" class="w-full max-w-md text-center">
      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-10">
        <div class="w-16 h-16 mx-auto mb-6 rounded-2xl flex items-center justify-center" style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)">
          <i class="pi pi-spin pi-spinner text-white text-2xl"></i>
        </div>
        <h2 class="text-lg font-bold text-gray-900 mb-2">Generando tu examen...</h2>
        <p class="text-sm text-gray-500 mb-6">El pipeline RAG está recuperando contexto relevante de tus documentos y los estándares del MEN</p>

        <div class="space-y-3 text-left">
          <div v-for="(step, i) in generationSteps" :key="i" class="flex items-center gap-3">
            <div class="w-5 h-5 shrink-0 flex items-center justify-center">
              <i v-if="i < currentStep" class="pi pi-check text-green-500 text-sm"></i>
              <i v-else-if="i === currentStep" class="pi pi-spin pi-spinner text-sky-500 text-sm"></i>
              <div v-else class="w-4 h-4 rounded-full border-2 border-gray-200"></div>
            </div>
            <span class="text-sm" :class="i < currentStep ? 'text-gray-400 line-through' : i === currentStep ? 'text-gray-900 font-medium' : 'text-gray-400'">
              {{ step }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado: Resultado -->
    <div v-else-if="view === 'result'" class="w-full max-w-3xl">

      <!-- Header resultado -->
      <div class="flex items-start justify-between mb-6 gap-4">
        <div>
          <h1 class="text-xl font-bold text-gray-900 leading-tight">{{ examResult?.title }}</h1>
          <p class="text-sm text-gray-500 mt-1">
            {{ examResult?.area }} · Grado {{ examResult?.grado }}° · {{ examResult?.questions.length }} preguntas
          </p>
          <div v-if="resultFiles.length" class="flex flex-wrap gap-1.5 mt-2">
            <button
              v-for="file in resultFiles"
              :key="file"
              class="flex items-center gap-1.5 bg-sky-50 border border-sky-200 rounded-lg px-2.5 py-1 text-xs text-sky-700 hover:bg-sky-100 transition-colors"
              @click="downloadAttachment(file)"
            >
              <span class="icon-[ic--twotone-description] w-3.5 h-3.5"></span>
              {{ file }}
              <span class="icon-[ic--twotone-download] w-3.5 h-3.5"></span>
            </button>
          </div>
        </div>
        <div class="flex gap-2 shrink-0">
          <Button
            label="Nuevo examen"
            icon="pi pi-plus"
            outlined
            size="small"
            @click="resetToGenerator"
          />
          <Button
            label="Exportar"
            icon="pi pi-download"
            size="small"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
            @click="exportMenu?.toggle($event)"
          />
          <Menu ref="exportMenu" :model="exportItems" popup />
        </div>
      </div>

      <!-- Preguntas -->
      <div class="space-y-4">
        <div
          v-for="(q, idx) in examResult?.questions"
          :key="idx"
          class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5"
        >
          <!-- Cabecera pregunta -->
          <div class="flex items-start gap-3 mb-3">
            <span class="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
              :class="questionTypeStyle(q.type).badge">
              {{ idx + 1 }}
            </span>
            <div class="flex-1">
              <span class="inline-block text-xs font-semibold px-2 py-0.5 rounded-full mb-2"
                :class="questionTypeStyle(q.type).chip">
                {{ questionTypeLabel(q.type) }}
              </span>
              <p class="text-sm font-medium text-gray-900 leading-relaxed">{{ q.stem }}</p>
            </div>
          </div>

          <!-- Opciones (múltiple choice / V-F) -->
          <div v-if="q.options?.length" class="ml-10 space-y-1.5">
            <div
              v-for="(opt, oi) in q.options"
              :key="oi"
              class="flex items-center gap-2.5 text-sm p-2 rounded-lg"
              :class="opt.correct ? 'bg-green-50 text-green-800 font-medium' : 'text-gray-600'"
            >
              <span class="w-5 h-5 rounded-full border flex items-center justify-center text-xs shrink-0 font-semibold"
                :class="opt.correct ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 text-gray-400'">
                {{ String.fromCharCode(65 + oi) }}
              </span>
              {{ opt.text }}
            </div>
          </div>

          <!-- Respuesta esperada (short_answer / essay) -->
          <div v-if="q.expected_answer" class="ml-10 mt-2 p-3 bg-sky-50 rounded-lg border border-sky-100">
            <p class="text-xs font-semibold text-sky-600 mb-1">Respuesta esperada</p>
            <p class="text-sm text-sky-800">{{ q.expected_answer }}</p>
          </div>

          <!-- Justificación -->
          <div v-if="q.justification" class="ml-10 mt-2 p-3 bg-amber-50 rounded-lg border border-amber-100">
            <p class="text-xs font-semibold text-amber-600 mb-1">Justificación</p>
            <p class="text-sm text-amber-800">{{ q.justification }}</p>
          </div>
        </div>
      </div>

      <p class="text-center text-xs text-gray-400 mt-6">
        Generado con Gemini 3.1 Flash Lite · Alineado con los EBC del MEN (Colombia)
      </p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

type View = 'generator' | 'generating' | 'result'
type QuestionType = 'multiple_choice' | 'true_false' | 'short_answer' | 'essay'

interface Option { text: string; correct: boolean }
interface Question {
  type: QuestionType
  stem: string
  options?: Option[]
  expected_answer?: string
  justification?: string
}
interface ExamResult {
  title: string
  area: string
  grado: string
  questions: Question[]
}

const view = ref<View>('generator')
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const currentStep = ref(0)
const examResult = ref<ExamResult | null>(null)
const resultExamId = ref<string | null>(null)
const resultFiles = ref<string[]>([])
const exportMenu = ref()

const form = reactive({
  title: '',
  area: null as string | null,
  grado: null as string | null,
  prompt: '',
  files: [] as File[],
  types: { multiple_choice: 3, true_false: 3, short_answer: 3, essay: 3 } as Record<string, number>,
})

const areas = [
  'Matemáticas', 'Lenguaje y Literatura', 'Ciencias Naturales',
  'Ciencias Sociales', 'Inglés', 'Filosofía', 'Tecnología e Informática',
]

const grados = [
  { label: 'Grado 9°', value: '9' },
  { label: 'Grado 10°', value: '10' },
  { label: 'Grado 11°', value: '11' },
]

const questionTypes = [
  { key: 'multiple_choice', label: 'Opción múltiple' },
  { key: 'true_false', label: 'Verdadero / Falso' },
  { key: 'short_answer', label: 'Respuesta corta' },
  { key: 'essay', label: 'Ensayo' },
]

const generationSteps = [
  'Extrayendo texto de los documentos',
  'Dividiendo en fragmentos (chunking)',
  'Generando embeddings semánticos',
  'Recuperando estándares MEN relevantes',
  'Construyendo el prompt enriquecido',
  'Generando preguntas con Gemini 3.1 Flash Lite',
]

const exportItems = [
  { label: 'PDF sin resolver', icon: 'pi pi-file-pdf', command: () => exportExam('pdf', false) },
  { label: 'PDF con soluciones', icon: 'pi pi-file-pdf', command: () => exportExam('pdf', true) },
  { separator: true },
  { label: 'Word sin resolver', icon: 'pi pi-file-word', command: () => exportExam('word', false) },
  { label: 'Word con soluciones', icon: 'pi pi-file-word', command: () => exportExam('word', true) },
]

const loadResultFiles = async (examId: string, hasFiles: boolean) => {
  if (!hasFiles) {
    resultFiles.value = []
    return
  }
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  try {
    resultFiles.value = await $fetch<string[]>(
      `${config.public.apiBase}/exams/${examId}/files`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` } }
    )
  } catch {
    resultFiles.value = []
  }
}

const downloadAttachment = async (filename: string) => {
  if (!resultExamId.value) return
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  try {
    const blob = await $fetch<Blob>(
      `${config.public.apiBase}/exams/${resultExamId.value}/files/${encodeURIComponent(filename)}`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` }, responseType: 'blob' }
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo descargar el archivo', life: 4000 })
  }
}

const exportExam = async (format: 'pdf' | 'word', includeSolutions: boolean) => {
  if (!resultExamId.value) return
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  try {
    const blob = await $fetch<Blob>(
      `${config.public.apiBase}/exams/${resultExamId.value}/${format}?include_solutions=${includeSolutions}`,
      { headers: { Authorization: `Bearer ${auth.accessToken}` }, responseType: 'blob' }
    )
    const ext = format === 'pdf' ? 'pdf' : 'docx'
    const suffix = includeSolutions ? 'con_soluciones' : 'sin_resolver'
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${examResult.value?.title ?? 'examen'}_${suffix}.${ext}`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo exportar el examen', life: 4000 })
  }
}

const totalQuestions = computed(() =>
  Object.values(form.types).reduce((a, b) => a + b, 0)
)

const questionTypeLabel = (type: QuestionType) => ({
  multiple_choice: 'Opción múltiple',
  true_false: 'Verdadero / Falso',
  short_answer: 'Respuesta corta',
  essay: 'Ensayo',
}[type])

const questionTypeStyle = (type: QuestionType) => ({
  multiple_choice: { badge: 'bg-sky-100 text-sky-700', chip: 'bg-sky-50 text-sky-600' },
  true_false:      { badge: 'bg-cyan-100 text-cyan-700', chip: 'bg-cyan-50 text-cyan-600' },
  short_answer:    { badge: 'bg-sky-100 text-sky-700',       chip: 'bg-sky-50 text-sky-600' },
  essay:           { badge: 'bg-amber-100 text-amber-700',   chip: 'bg-amber-50 text-amber-600' },
}[type])

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) form.files.push(...Array.from(input.files))
}

const onDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files) form.files.push(...Array.from(e.dataTransfer.files))
}

const removeFile = (index: number) => {
  form.files.splice(index, 1)
}

const resetToGenerator = () => {
  view.value = 'generator'
  examResult.value = null
  examStore.currentExam = null
}

const examStore = useExamStore()

const toast = useToast()

watch(() => examStore.currentExam, (exam) => {
  if (exam && exam.result) {
    examResult.value = exam.result
    resultExamId.value = exam.id
    loadResultFiles(exam.id, !!exam.files_uuid)
    // Aseguramos que el resultado tenga la info del examen para el header
    if (examResult.value) {
      examResult.value.area = exam.area
      examResult.value.grado = exam.grado
    }
    view.value = 'result'
  } else if (exam && !exam.result) {
    toast.add({
      severity: 'warn',
      summary: 'Sin resultado',
      detail: exam.status === 'failed' ? 'La generación de este examen falló' : 'Este examen aún se está generando',
      life: 3500,
    })
  } else if (exam === null) {
    view.value = 'generator'
    examResult.value = null
  }
}, { immediate: true })

const generateExam = async () => {
  if (!form.area || !form.grado) return
  
  view.value = 'generating'
  currentStep.value = 0
  
  try {
    // 1. Subir documentos del docente a R2 (si hay)
    let filesUuid: string | undefined
    if (form.files.length) {
      const upload = await examStore.uploadFiles(form.files)
      filesUuid = upload.files_uuid
    }

    // 2. Iniciar generación
    const qTypes = Object.entries(form.types)
      .filter(([_, qty]) => qty > 0)
      .map(([type, quantity]) => ({ type, quantity }))

    const examRequest = {
      title: form.title || `Examen de ${form.area}`,
      area: form.area,
      grado: form.grado,
      prompt: form.prompt,
      num_questions: totalQuestions.value,
      question_types: qTypes,
      files_uuid: filesUuid
    }

    const initialExam = await examStore.generate(examRequest)
    
    // 2. Polling
    let status = initialExam.status
    currentStep.value = 1
    
    while (status === 'pending' || status === 'processing') {
      await new Promise(r => setTimeout(r, 3000))
      const statusData = await examStore.getStatus(initialExam.id)
      status = statusData.status as any
      
      if (status === 'processing' && currentStep.value < 4) {
        currentStep.value++
      }
    }

    if (status === 'successful') {
      currentStep.value = 6
      const finalExam = await examStore.getExam(initialExam.id)
      examStore.currentExam = finalExam
      const idx = examStore.exams.findIndex(e => e.id === finalExam.id)
      if (idx !== -1) examStore.exams[idx] = finalExam
      examResult.value = finalExam.result
      resultExamId.value = finalExam.id
      loadResultFiles(finalExam.id, !!finalExam.files_uuid)
      form.files = []
      // Aseguramos que el resultado tenga la info del examen para el header
      if (examResult.value) {
        examResult.value.area = finalExam.area
        examResult.value.grado = finalExam.grado
      }
      view.value = 'result'
    } else {
      throw new Error('La generación del examen falló')
    }
    
  } catch (err) {
    console.error(err)
    alert('Error al generar el examen. Por favor intenta de nuevo.')
    view.value = 'generator'
  }
}
</script>
