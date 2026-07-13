<template>
  <div class="min-h-full flex flex-col items-center justify-center px-4 py-12">
    <div class="w-full max-w-2xl">

      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Mi Perfil</h1>
        <p class="text-sm text-gray-500 mt-1">Gestiona tu información personal y preferencias</p>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">

        <!-- Avatar -->
        <div class="p-6 border-b border-gray-100 flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-sky-400 to-sky-600 text-white text-2xl font-bold flex items-center justify-center shrink-0">
            {{ initials }}
          </div>
          <div>
            <p class="text-lg font-bold text-gray-900">{{ form.fullName || '—' }}</p>
            <p class="text-sm text-gray-400">{{ roleLabel }}</p>
          </div>
        </div>

        <!-- Formulario -->
        <form class="p-6 space-y-4" @submit.prevent="onSave">
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Nombre completo</label>
            <InputText v-model="form.fullName" fluid />
          </div>
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Correo electrónico</label>
            <InputText :model-value="form.email" type="email" fluid disabled />
            <p class="text-xs text-gray-400 mt-1">El correo no se puede modificar.</p>
          </div>

          <div class="pt-2 flex justify-end">
            <Button
              type="submit"
              label="Guardar cambios"
              :loading="saving"
              :disabled="!canSave"
              style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
            />
          </div>
        </form>

        <!-- Cambiar contraseña -->
        <div class="px-6 pb-6 border-t border-gray-100 pt-4">
          <p class="text-xs font-semibold text-gray-500 mb-3">Cambiar contraseña</p>
          <div class="space-y-3">
            <div>
              <label class="text-xs text-gray-400 mb-1 block">Contraseña actual</label>
              <Password v-model="passwordForm.current" :feedback="false" toggle-mask fluid input-class="w-full" />
            </div>
            <div>
              <label class="text-xs text-gray-400 mb-1 block">Nueva contraseña</label>
              <Password v-model="passwordForm.new" toggle-mask fluid input-class="w-full" />
              <p class="text-xs text-gray-400 mt-1">Mínimo 8 caracteres.</p>
            </div>
            <div class="flex justify-end">
              <Button
                label="Actualizar contraseña"
                outlined
                :loading="changingPassword"
                :disabled="!canChangePassword"
                @click="onChangePassword"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const auth = useAuthStore()
const toast = useToast()
const saving = ref(false)
const changingPassword = ref(false)

const form = reactive({
  fullName: '',
  email: '',
})

const passwordForm = reactive({ current: '', new: '' })

function syncFromUser() {
  form.fullName = auth.user?.full_name ?? ''
  form.email = auth.user?.email ?? ''
}

onMounted(async () => {
  if (!auth.user) await auth.fetchUser()
  syncFromUser()
})

watch(() => auth.user, syncFromUser)

const initials = computed(() => {
  const parts = form.fullName.trim().split(/\s+/).filter(Boolean)
  return ((parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')).toUpperCase() || '?'
})

const roleLabel = computed(() => (auth.user?.role === 'admin' ? 'Administrador' : 'Docente'))

const canSave = computed(() =>
  !!form.fullName.trim() && form.fullName.trim() !== (auth.user?.full_name ?? '')
)

const canChangePassword = computed(() =>
  !!passwordForm.current && passwordForm.new.length >= 8
)

const onSave = async () => {
  if (!canSave.value) return
  saving.value = true
  try {
    await auth.updateProfile(form.fullName.trim())
    toast.add({ severity: 'success', summary: 'Cambios guardados', life: 3000 })
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err?.data?.detail ?? 'No se pudo guardar', life: 4000 })
  } finally {
    saving.value = false
  }
}

const onChangePassword = async () => {
  if (!canChangePassword.value) return
  changingPassword.value = true
  try {
    await auth.changePassword(passwordForm.current, passwordForm.new)
    passwordForm.current = ''
    passwordForm.new = ''
    toast.add({ severity: 'success', summary: 'Contraseña actualizada', life: 3000 })
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err?.data?.detail ?? 'No se pudo actualizar la contraseña', life: 4000 })
  } finally {
    changingPassword.value = false
  }
}
</script>
