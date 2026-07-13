<template>
  <div class="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-slate-50 to-sky-50/30">
    <div class="w-full max-w-sm">

      <div class="text-center mb-8">
        <AppLogo :height="40" class="mx-auto mb-4" />
        <h2 class="text-2xl font-bold text-gray-900">Nueva contraseña</h2>
        <p class="text-sm text-gray-500 mt-1">Elige una contraseña segura para tu cuenta</p>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">

        <!-- Token inválido o expirado -->
        <div v-if="tokenInvalid" class="text-center py-4">
          <div class="w-14 h-14 rounded-2xl bg-red-50 border border-red-100 flex items-center justify-center mx-auto mb-4">
            <i class="pi pi-times-circle text-red-400 text-2xl"></i>
          </div>
          <h3 class="font-semibold text-gray-900 mb-2">Enlace inválido o expirado</h3>
          <p class="text-sm text-gray-500">El enlace de recuperación ya no es válido. Puedes solicitar uno nuevo.</p>
          <NuxtLink to="/forgot-password" class="inline-block mt-5 text-sm text-sky-600 font-semibold hover:underline">
            Solicitar nuevo enlace
          </NuxtLink>
        </div>

        <!-- Éxito -->
        <div v-else-if="done" class="text-center py-4">
          <div class="w-14 h-14 rounded-2xl bg-green-50 border border-green-100 flex items-center justify-center mx-auto mb-4">
            <i class="pi pi-check-circle text-green-500 text-2xl"></i>
          </div>
          <h3 class="font-semibold text-gray-900 mb-2">¡Contraseña actualizada!</h3>
          <p class="text-sm text-gray-500">Ya puedes iniciar sesión con tu nueva contraseña.</p>
          <NuxtLink to="/login" class="inline-block mt-5 text-sm text-sky-600 font-semibold hover:underline">
            Iniciar sesión
          </NuxtLink>
        </div>

        <!-- Formulario -->
        <form v-else class="space-y-4" @submit.prevent="onSubmit">
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Nueva contraseña</label>
            <Password
              v-model="form.password"
              placeholder="Mínimo 8 caracteres"
              toggle-mask
              fluid
              input-class="w-full"
              autocomplete="new-password"
            />
          </div>
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Repetir contraseña</label>
            <Password
              v-model="form.confirm"
              placeholder="Repite tu contraseña"
              :feedback="false"
              toggle-mask
              fluid
              input-class="w-full"
              autocomplete="new-password"
            />
          </div>
          <Message v-if="error" severity="error" :closable="false" class="text-sm">{{ error }}</Message>
          <Button
            type="submit"
            label="Cambiar contraseña"
            :loading="loading"
            fluid
            class="!mt-2"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
          />
        </form>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const config = useRuntimeConfig()
const route = useRoute()

const token = computed(() => route.query.token as string | undefined)
const tokenInvalid = ref(false)
const done = ref(false)
const loading = ref(false)
const error = ref('')
const form = reactive({ password: '', confirm: '' })

onMounted(() => {
  if (!token.value) tokenInvalid.value = true
})

const onSubmit = async () => {
  error.value = ''
  if (form.password.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }
  if (form.password !== form.confirm) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }
  loading.value = true
  try {
    const body = new FormData()
    body.append('token', token.value!)
    body.append('password', form.password)
    await $fetch(`${config.public.apiBase}/auth/reset-password`, { method: 'POST', body })
    done.value = true
  } catch (err: any) {
    const detail = err?.data?.detail
    if (detail === 'El enlace es inválido o ya expiró') {
      tokenInvalid.value = true
    } else {
      error.value = 'Ocurrió un error. Intenta de nuevo.'
    }
  } finally {
    loading.value = false
  }
}
</script>
