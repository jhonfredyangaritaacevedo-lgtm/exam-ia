<template>
  <div class="h-screen flex flex-col overflow-hidden bg-gradient-to-br from-slate-50 to-sky-50/30">

    <!-- Header fijo -->
    <header class="h-14 shrink-0 bg-white/95 backdrop-blur-md border-b border-gray-200 flex items-center px-3 gap-2 z-50">
      <Button
        :icon="sidebarOpen ? 'pi pi-angle-left' : 'pi pi-bars'"
        text rounded size="small"
        class="text-gray-500"
        @click="toggleSidebar"
      />
      <NuxtLink to="/" class="flex items-center">
        <AppLogo :height="36" />
      </NuxtLink>

      <div class="flex-1" />

      <button
        @click="toggleUserMenu"
        class="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-sky-600 text-white text-xs font-bold flex items-center justify-center hover:shadow-md hover:shadow-sky-200 transition-shadow"
      >
        {{ initials }}
      </button>
      <Menu ref="userMenuRef" :model="userMenuItems" popup />
    </header>

    <!-- Cuerpo principal -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Sidebar Desktop -->
      <aside
        class="hidden lg:flex flex-col bg-white border-r border-gray-200 shrink-0 overflow-hidden transition-all duration-300 ease-in-out"
        :style="{ width: sidebarOpen ? '280px' : '0px' }"
      >
        <div class="flex flex-col h-full w-[280px]">
          <!-- Nuevo Examen -->
          <div class="p-3 border-b border-gray-100">
            <button
              @click="newExam"
              class="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-white text-sm font-semibold transition-all hover:opacity-90 hover:shadow-md hover:shadow-sky-200"
              style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)"
            >
              <i class="pi pi-plus text-xs"></i>
              Nuevo Examen
            </button>
          </div>

          <!-- Historial -->
          <div class="flex-1 overflow-y-auto p-2">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2 py-2">Historial</p>

            <div
              v-for="exam in examHistory"
              :key="exam.id"
              class="group flex items-start justify-between p-2.5 rounded-lg cursor-pointer transition-colors mb-0.5"
              :class="selectedExamId === exam.id ? 'bg-sky-50 text-sky-900' : 'hover:bg-gray-100'"
              @click="selectExam(exam)"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium truncate leading-snug"
                  :class="selectedExamId === exam.id ? 'text-sky-900' : 'text-gray-800'">
                  {{ exam.title }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5 truncate">
                  {{ exam.area }} · {{ exam.grado }}° · {{ exam.num_questions }} preg.
                </p>
              </div>
              <Button
                icon="pi pi-trash"
                text rounded size="small" severity="danger"
                class="opacity-0 group-hover:opacity-100 transition-opacity shrink-0 !p-1 !w-6 !h-6"
                @click.stop="confirmDelete(exam)"
              />
            </div>

            <div v-if="examHistory.length === 0" class="text-center py-10">
              <i class="pi pi-inbox text-3xl text-gray-200 block mb-2"></i>
              <p class="text-sm text-gray-400">Aún no hay exámenes</p>
            </div>
          </div>

          <!-- Usuario -->
          <div class="p-3 border-t border-gray-100 flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-sky-400 to-sky-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
              {{ initials }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate leading-none">{{ userName }}</p>
              <p class="text-xs text-gray-400 mt-0.5">Docente</p>
            </div>
            <Button icon="pi pi-cog" text rounded size="small" class="text-gray-400 !p-1" @click="navigateTo('/profile')" />
          </div>
        </div>
      </aside>

      <!-- Sidebar Mobile (Drawer) -->
      <Drawer
        v-model:visible="mobileSidebarOpen"
        position="left"
        :header="false"
        class="!w-72"
        :pt="{ content: { class: '!p-0 flex flex-col h-full' } }"
      >
        <div class="flex flex-col h-full">
          <div class="p-3 border-b border-gray-100">
            <button
              @click="() => { newExam(); mobileSidebarOpen = false }"
              class="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-white text-sm font-semibold"
              style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)"
            >
              <i class="pi pi-plus text-xs"></i>
              Nuevo Examen
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-2">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2 py-2">Historial</p>

            <div
              v-for="exam in examHistory"
              :key="exam.id"
              class="group flex items-start justify-between p-2.5 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors mb-0.5"
              :class="{ 'bg-sky-50': selectedExamId === exam.id }"
              @click="() => { selectExam(exam); mobileSidebarOpen = false }"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-800 truncate">{{ exam.title }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ exam.area }} · {{ exam.grado }}° · {{ exam.num_questions }} preg.</p>
              </div>
            </div>

            <div v-if="examHistory.length === 0" class="text-center py-10">
              <i class="pi pi-inbox text-3xl text-gray-200 block mb-2"></i>
              <p class="text-sm text-gray-400">Aún no hay exámenes</p>
            </div>
          </div>

          <div class="p-3 border-t border-gray-100 flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-sky-400 to-sky-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
              {{ initials }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate">{{ userName }}</p>
              <p class="text-xs text-gray-400">Docente</p>
            </div>
          </div>
        </div>
      </Drawer>

      <!-- Mobile sidebar toggle (fab) -->
      <button
        class="lg:hidden fixed bottom-5 left-4 z-40 w-11 h-11 rounded-full bg-white shadow-lg border border-gray-200 flex items-center justify-center text-gray-600"
        @click="mobileSidebarOpen = true"
      >
        <i class="pi pi-history"></i>
      </button>

      <!-- Contenido principal -->
      <main class="flex-1 overflow-y-auto">
        <slot />
      </main>
    </div>

    <Toast position="top-right" />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from 'primevue/useconfirm'

const confirm = useConfirm()
const auth = useAuthStore()
const sidebarOpen = ref(true)
const mobileSidebarOpen = ref(false)
const selectedExamId = ref<string | null>(null)
const userMenuRef = ref()

const examStore = useExamStore()
const userName = computed(() => auth.user?.full_name ?? '')
const initials = computed(() =>
  userName.value.split(' ').filter(Boolean).map(n => n[0]).slice(0, 2).join('').toUpperCase()
)

const examHistory = computed(() => examStore.exams)

onMounted(() => {
  examStore.fetchExams()
})

const userMenuItems = computed(() => [
  { label: userName.value, disabled: true, class: 'text-xs text-gray-400' },
  { separator: true },
  { label: 'Mi Perfil', icon: 'pi pi-user', command: () => navigateTo('/profile') },
  ...(auth.user?.role === 'admin' ? [
    { label: 'Administrar RAG', icon: 'pi pi-database', command: () => navigateTo('/admin/rag') },
  ] : []),
  { separator: true },
  { label: 'Cerrar Sesión', icon: 'pi pi-sign-out', command: () => auth.logout() },
])

const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleUserMenu = (e: Event) => userMenuRef.value?.toggle(e)

const newExam = () => {
  selectedExamId.value = null
  examStore.currentExam = null
  navigateTo('/')
}

const selectExam = (exam: any) => {
  selectedExamId.value = exam.id
  examStore.currentExam = exam
  navigateTo('/')
}

const confirmDelete = (exam: any) => {
  confirm.require({
    message: `¿Eliminar "${exam.title}"?`,
    header: 'Confirmar',
    icon: 'pi pi-trash',
    rejectLabel: 'Cancelar',
    acceptLabel: 'Eliminar',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await examStore.deleteExam(exam.id)
      if (selectedExamId.value === exam.id) selectedExamId.value = null
    },
  })
}
</script>
