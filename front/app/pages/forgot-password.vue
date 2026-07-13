<template>
  <div class="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-slate-50 to-sky-50/30">
    <div class="w-full max-w-sm">

      <div class="text-center mb-8">
        <AppLogo :height="40" class="mx-auto mb-4" />
        <h2 class="text-2xl font-bold text-gray-900">Recuperar contraseña</h2>
        <p class="text-sm text-gray-500 mt-1">Te enviaremos un enlace a tu correo</p>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">

        <div v-if="sent" class="text-center py-4">
          <div class="w-14 h-14 rounded-2xl bg-green-50 border border-green-100 flex items-center justify-center mx-auto mb-4">
            <i class="pi pi-envelope text-green-500 text-2xl"></i>
          </div>
          <h3 class="font-semibold text-gray-900 mb-2">Revisa tu correo</h3>
          <p class="text-sm text-gray-500 leading-relaxed">
            Si el correo está registrado, recibirás un enlace para restablecer tu contraseña. El enlace expira en 10 minutos.
          </p>
          <NuxtLink to="/login" class="inline-block mt-5 text-sm text-sky-600 font-semibold hover:underline">
            Volver al inicio de sesión
          </NuxtLink>
        </div>

        <form v-else class="space-y-4" @submit.prevent="onSubmit">
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Correo electrónico</label>
            <InputText
              v-model="email"
              type="email"
              placeholder="tu@correo.com"
              fluid
              autocomplete="email"
            />
          </div>
          <Message v-if="error" severity="error" :closable="false" class="text-sm">{{ error }}</Message>
          <Button
            type="submit"
            label="Enviar enlace"
            icon="pi pi-send"
            icon-pos="right"
            :loading="loading"
            fluid
            class="!mt-2"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
          />
          <p class="text-center text-sm text-gray-400">
            <NuxtLink to="/login" class="text-sky-600 font-semibold hover:underline">
              Volver al inicio de sesión
            </NuxtLink>
          </p>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const config = useRuntimeConfig()

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)

const onSubmit = async () => {
  error.value = ''
  if (!email.value) {
    error.value = 'Por favor ingresa tu correo.'
    return
  }
  loading.value = true
  try {
    const form = new FormData()
    form.append('email', email.value)
    await $fetch(`${config.public.apiBase}/auth/forgot-password`, { method: 'POST', body: form })
    sent.value = true
  } catch {
    error.value = 'Ocurrió un error. Intenta de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>
