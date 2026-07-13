<template>
  <div class="min-h-screen flex">

    <!-- Panel izquierdo — branding -->
    <div
      class="hidden lg:flex lg:w-1/2 xl:w-[55%] flex-col justify-between p-12 relative overflow-hidden"
      style="background: linear-gradient(145deg, #0EA5E9 0%, #0284C7 55%, #075985 100%)"
    >
      <!-- Círculos decorativos de fondo -->
      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full opacity-10 bg-white" />
      <div class="absolute -bottom-32 -right-20 w-[480px] h-[480px] rounded-full opacity-10 bg-white" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full opacity-5 bg-white" />

      <!-- Logo -->
      <div class="relative z-10">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-xl bg-white/20 flex items-center justify-center">
            <span class="icon-[ic--twotone-fact-check] w-7 h-7 text-white" />
          </div>
          <span class="text-2xl font-extrabold text-white tracking-tight">Exam<span class="text-sky-200">IA</span></span>
        </div>
      </div>

      <!-- Contenido central -->
      <div class="relative z-10 space-y-8">
        <div>
          <h1 class="text-4xl font-extrabold text-white leading-tight mb-4">
            Genera exámenes inteligentes en segundos
          </h1>
          <p class="text-sky-100 text-lg leading-relaxed">
            Sube tus materiales de clase y la IA crea preguntas alineadas con los Estándares Básicos de Competencias del MEN.
          </p>
        </div>

        <!-- Feature pills -->
        <div class="space-y-3">
          <div v-for="f in features" :key="f.text" class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-white/15 flex items-center justify-center shrink-0">
              <span :class="f.icon + ' w-5 h-5 text-sky-100'" />
            </div>
            <span class="text-sky-50 text-sm font-medium">{{ f.text }}</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <p class="relative z-10 text-sky-300 text-xs">
        ExamIA · Para educación media colombiana · Grados 9° – 11°
      </p>
    </div>

    <!-- Panel derecho — formulario -->
    <div class="flex-1 flex flex-col items-center justify-center px-6 py-12 bg-white">

      <!-- Logo (solo mobile) -->
      <div class="lg:hidden mb-8">
        <AppLogo :height="38" class="mx-auto" />
      </div>

      <div class="w-full max-w-sm">

        <!-- Encabezado -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ activeTab === 'login' ? 'Bienvenido de nuevo' : 'Crea tu cuenta' }}
          </h2>
          <p class="text-sm text-gray-500 mt-1">
            {{ activeTab === 'login'
              ? 'Ingresa tus credenciales para continuar'
              : 'Completa el formulario para comenzar' }}
          </p>
        </div>

        <!-- Tabs -->
        <div class="flex bg-gray-100 rounded-xl p-1 mb-6">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
            :class="activeTab === tab.key
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Login -->
        <form v-if="activeTab === 'login'" class="space-y-4" @submit.prevent="onLogin">
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Correo electrónico</label>
            <InputText
              v-model="loginForm.email"
              type="email"
              placeholder="tu@correo.com"
              fluid
              autocomplete="email"
            />
          </div>
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs font-semibold text-gray-500">Contraseña</label>
              <NuxtLink to="/forgot-password" class="text-xs text-sky-600 hover:underline">
                ¿Olvidaste tu contraseña?
              </NuxtLink>
            </div>
            <Password
              v-model="loginForm.password"
              placeholder="••••••••"
              :feedback="false"
              toggle-mask
              fluid
              input-class="w-full"
              autocomplete="current-password"
            />
          </div>
          <Message v-if="loginError" severity="error" :closable="false" class="text-sm">{{ loginError }}</Message>
          <Button
            type="submit"
            label="Iniciar sesión"
            :loading="loginLoading"
            fluid
            class="!mt-6"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
          />
          <p class="text-center text-sm text-gray-400 mt-4">
            ¿No tienes cuenta?
            <button type="button" class="text-sky-600 font-semibold hover:underline" @click="activeTab = 'register'">
              Regístrate
            </button>
          </p>
        </form>

        <!-- Register -->
        <form v-else class="space-y-4" @submit.prevent="onRegister">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Nombre</label>
              <InputText v-model="registerForm.firstName" placeholder="Juan" fluid />
            </div>
            <div>
              <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Apellido</label>
              <InputText v-model="registerForm.lastName" placeholder="Pérez" fluid />
            </div>
          </div>
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Correo electrónico</label>
            <InputText v-model="registerForm.email" type="email" placeholder="tu@correo.com" fluid autocomplete="email" />
          </div>
          <div>
            <label class="text-xs font-semibold text-gray-500 mb-1.5 block">Contraseña</label>
            <Password
              v-model="registerForm.password"
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
              v-model="registerForm.confirmPassword"
              placeholder="Repite tu contraseña"
              :feedback="false"
              toggle-mask
              fluid
              input-class="w-full"
              autocomplete="new-password"
            />
          </div>
          <Message v-if="registerError" severity="error" :closable="false" class="text-sm">{{ registerError }}</Message>
          <Button
            type="submit"
            label="Crear cuenta"
            :loading="registerLoading"
            fluid
            class="!mt-2"
            style="background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none;"
          />
          <p class="text-center text-sm text-gray-400">
            ¿Ya tienes cuenta?
            <button type="button" class="text-sky-600 font-semibold hover:underline" @click="activeTab = 'login'">
              Inicia sesión
            </button>
          </p>
        </form>

      </div>

      <p class="mt-12 text-xs text-gray-300">
        © 2025 ExamIA · Todos los derechos reservados
      </p>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const auth = useAuthStore()

const activeTab = ref<'login' | 'register'>('login')

const tabs = [
  { key: 'login', label: 'Iniciar sesión' },
  { key: 'register', label: 'Registrarse' },
]

const features = [
  { icon: 'icon-[ic--twotone-upload-file]',    text: 'Sube PDF, Word o PowerPoint de tus clases' },
  { icon: 'icon-[ic--twotone-psychology]',      text: 'Pipeline RAG con embeddings semánticos' },
  { icon: 'icon-[ic--twotone-fact-check]',      text: 'Alineado con los EBC del MEN Colombia' },
  { icon: 'icon-[ic--twotone-auto-awesome]',    text: 'Generado por Gemini 2.5 Flash' },
]

const loginForm = reactive({ email: '', password: '' })
const loginError = ref('')
const loginLoading = ref(false)

const registerForm = reactive({
  firstName: '', lastName: '', email: '', password: '', confirmPassword: '',
})
const registerError = ref('')
const registerLoading = ref(false)

const onLogin = async () => {
  loginError.value = ''
  if (!loginForm.email || !loginForm.password) {
    loginError.value = 'Por favor completa todos los campos.'
    return
  }
  loginLoading.value = true
  try {
    await auth.login(loginForm.email, loginForm.password)
    navigateTo('/')
  } catch (err: any) {
    const msg = err?.data?.detail
    loginError.value = msg === 'Incorrect email or password'
      ? 'Correo o contraseña incorrectos.'
      : 'Error al iniciar sesión. Intenta de nuevo.'
  } finally {
    loginLoading.value = false
  }
}

const onRegister = async () => {
  registerError.value = ''
  const { firstName, lastName, email, password, confirmPassword } = registerForm
  if (!firstName || !lastName || !email || !password || !confirmPassword) {
    registerError.value = 'Por favor completa todos los campos.'
    return
  }
  if (password.length < 8) {
    registerError.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }
  if (password !== confirmPassword) {
    registerError.value = 'Las contraseñas no coinciden.'
    return
  }
  registerLoading.value = true
  try {
    await auth.register(`${firstName} ${lastName}`, email, password)
    navigateTo('/')
  } catch (err: any) {
    const msg = err?.data?.detail
    registerError.value = msg === 'Email already registered'
      ? 'Este correo ya está registrado.'
      : 'Error al crear la cuenta. Intenta de nuevo.'
  } finally {
    registerLoading.value = false
  }
}
</script>
