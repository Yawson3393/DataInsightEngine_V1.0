<template>
  <div class="page">
    <h2>系统总览</h2>

    <TimeseriesChart
      title="堆级 V / I / SOC / SOH"
      :series="summarySeries" />

    <h3 style="margin-top: 20px">温度分布（热力图）</h3>
    <Heatmap :matrix="temperatureMatrix" />

    <h3 style="margin-top: 20px">簇总览（电压）</h3>
    <Heatmap :matrix="rackVoltageMatrix" />

    <h3 style="margin-top: 20px">异常摘要</h3>
    <a-list bordered>
      <a-list-item v-for="item in anomalies" :key="item">{{ item }}</a-list-item>
    </a-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getOverview } from '@/api'
import Heatmap from './Heatmap.vue'
import TimeseriesChart from './TimeseriesChart.vue'

const temperatureMatrix = ref<number[][]>([])
const rackVoltageMatrix = ref<number[][]>([])
const summarySeries = ref<any[]>([])
const anomalies = ref<string[]>([])

async function load() {
  const r = await api.getOverview()

  summarySeries.value = r.timeseries
  temperatureMatrix.value = r.temp_matrix
  rackVoltageMatrix.value = r.rack_voltage
  anomalies.value = r.anomalies
}

onMounted(load)
</script>

<style scoped>
.page { padding: 20px; }
</style>
