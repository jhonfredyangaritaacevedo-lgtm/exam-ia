<template>
  <div class="inline-flex items-center gap-2" v-bind="$attrs">
    <!-- Caja con gradiente + icono two-tone -->
    <div
      class="rounded-xl flex items-center justify-center shrink-0"
      :style="{
        width: `${height}px`,
        height: `${height}px`,
        background: 'linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)',
      }"
    >
      <span
        class="icon-[ic--twotone-fact-check]"
        :style="{ width: `${iconSz}px`, height: `${iconSz}px`, color: 'white' }"
      />
    </div>
    <!-- Wordmark -->
    <span
      v-if="!iconOnly"
      class="font-extrabold text-gray-900 leading-none select-none tracking-tight"
      :style="{ fontSize: `${wordSz}px` }"
    >Exam<span style="color: #0284C7">IA</span></span>
  </div>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<{
  iconOnly?: boolean
  height?: number
}>(), {
  iconOnly: false,
  height: 36,
})

const iconSz = computed(() => Math.round(props.height * 0.6))
const wordSz = computed(() => Math.round(props.height * 0.72))
</script>
