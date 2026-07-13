import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const config = useRuntimeConfig()
  const accessToken = useCookie<string | null>('auth_access_token', {
    maxAge: 60 * 60 * 24, // 1 day
    sameSite: 'lax',
  })
  const refreshToken = useCookie<string | null>('auth_refresh_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 days
    sameSite: 'lax',
  })
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!accessToken.value)

  async function login(email: string, password: string) {
    const form = new FormData()
    form.append('email', email)
    form.append('password', password)

    const data = await $fetch<{ access_token: string; refresh_token: string; token_type: string }>(
      `${config.public.apiBase}/auth/login`,
      { method: 'POST', body: form },
    )
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    await fetchUser()
  }

  async function register(fullName: string, email: string, password: string) {
    const form = new FormData()
    form.append('full_name', fullName)
    form.append('email', email)
    form.append('password', password)

    await $fetch<User>(
      `${config.public.apiBase}/auth/register`,
      { method: 'POST', body: form },
    )
    await login(email, password)
  }

  async function refresh() {
    if (!refreshToken.value) return logout()
    
    try {
      const form = new FormData()
      form.append('refresh_token', refreshToken.value)
      
      const data = await $fetch<{ access_token: string; refresh_token: string }>(
        `${config.public.apiBase}/auth/refresh`,
        { method: 'POST', body: form }
      )
      
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
    } catch {
      logout()
    }
  }

  async function fetchUser() {
    if (!accessToken.value) return
    try {
      const data = await $fetch<User>(`${config.public.apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken.value}` },
      })
      user.value = data
    } catch (err: any) {
      if (err.status === 401 && refreshToken.value) {
        await refresh()
        if (accessToken.value) return fetchUser()
      }
      logout()
    }
  }

  async function updateProfile(fullName: string) {
    const form = new FormData()
    form.append('full_name', fullName)
    const data = await $fetch<User>(`${config.public.apiBase}/auth/me`, {
      method: 'PATCH',
      body: form,
      headers: { Authorization: `Bearer ${accessToken.value}` },
    })
    user.value = data
    return data
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    const form = new FormData()
    form.append('current_password', currentPassword)
    form.append('new_password', newPassword)
    return await $fetch<{ message: string }>(`${config.public.apiBase}/auth/change-password`, {
      method: 'POST',
      body: form,
      headers: { Authorization: `Bearer ${accessToken.value}` },
    })
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    navigateTo('/login')
  }

  return { accessToken, refreshToken, user, isLoggedIn, login, register, fetchUser, updateProfile, changePassword, logout }
})
