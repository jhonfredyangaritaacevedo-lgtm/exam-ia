const PUBLIC_PATHS = ['/login', '/forgot-password', '/reset-password']

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  if (!auth.isLoggedIn && !PUBLIC_PATHS.includes(to.path)) {
    return navigateTo('/login')
  }

  if (auth.isLoggedIn && PUBLIC_PATHS.includes(to.path)) {
    return navigateTo('/')
  }
})
