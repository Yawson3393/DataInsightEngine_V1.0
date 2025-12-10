<template>
  <div class="page">
    <h2>任务进度</h2>

    <div v-if="!connected">正在连接进度流...</div>

    <a-progress
      v-if="connected"
      :percent="progress"
      status="active"
      style="width: 400px" />

    <h3 style="margin-top: 20px">实时日志</h3>

    <LogViewer :lines="logs" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LogViewer from './LogViewer.vue'

const logs = ref<string[]>([])
const progress = ref(0)
const connected = ref(false)

const jobId = new URLSearchParams(location.search).get('job')

onMounted(() => {
  const ws = new WebSocket(`ws://127.0.0.1:8001/api/ws/progress/${jobId}`)
  ws.onopen = () => (connected.value = true)

  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data)

    if (msg.type === 'progress') {
      progress.value = msg.value
    }

    if (msg.type === 'log') {
      logs.value.push(msg.text)
    }
  }
})
</script>

<style scoped>
.page { padding: 20px; }
</style>
