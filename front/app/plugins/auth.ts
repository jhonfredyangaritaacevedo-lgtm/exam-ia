export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  if (auth.isLoggedIn && !auth.user) {
    await auth.fetchUser()
  }
})
