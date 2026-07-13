import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  ssr: false,

  nitro: {
    preset: 'cloudflare_module'
  },

  app: {
    head: {
      title: 'ExamIA — Generador Inteligente de Exámenes',
      meta: [
        { name: 'description', content: 'Plataforma de generación automática de exámenes para educación media colombiana con Inteligencia Artificial.' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/logo-icon.svg' },
      ],
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },

  modules: [
    '@primevue/nuxt-module',
    '@pinia/nuxt',
  ],

  primevue: {
    importTheme: { from: '~/assets/themes/theme.js' },
  },

  css: ['~/assets/css/main.css'],

  vite: {
    plugins: [
      tailwindcss()
    ],
    optimizeDeps: {
      include: [
        '@vue/devtools-core',
        '@vue/devtools-kit',
      ]
    }
  }
})
