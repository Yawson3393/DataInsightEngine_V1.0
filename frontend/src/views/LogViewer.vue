<template>
  <div class="log-box">
    <pre v-for="(l, i) in lines" :key="i">{{ l }}</pre>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ lines: string[] }>()
</script>

<style scoped>
.log-box {
  background: #111;
  color: #0f0;
  padding: 10px;
  height: 300px;
  overflow-y: scroll;
}
</style>
