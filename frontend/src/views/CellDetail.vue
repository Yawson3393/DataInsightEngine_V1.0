<template>
  <div class="page">
    <h2>电池单体详情（Cell {{ cellId }}）</h2>

    <TimeseriesChart title="电压时序" :series="volSeries" />
    <TimeseriesChart title="温度时序" :series="tempSeries" />

    <h3 style="margin-top: 20px">SOH / EOL 预测</h3>
    <TimeseriesChart :series="sohSeries" />

    <h3 style="margin-top: 20px">特征图（dV/dt）</h3>
    <TimeseriesChart :series="featureSeries" />

    <h3 style="margin-top: 20px">健康雷达图</h3>
    <div id="radar" style="width: 400px; height: 300px"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getCellDetail } from '@/api'
import TimeseriesChart from './TimeseriesChart.vue'

const route = useRoute()
const rackId = route.params.rack as string
const moduleId = route.params.module as string
const cellId = route.params.cell as string

const volSeries = ref([])
const tempSeries = ref([])
const sohSeries = ref([])
const featureSeries = ref([])
const radarData = ref<any[]>([])
const radarIndicator = ref<any[]>([])
const radarValue = ref<number[]>([])

async function load() {
  try {
    const r = await getCellDetail(rackId, moduleId, cellId)
    volSeries.value = r.voltage || []
    tempSeries.value = r.temperature || []
    sohSeries.value = r.soh || []
    featureSeries.value = r.features || []
    radarData.value = r.radar || []

    // 减少重复计算
    radarIndicator.value = radarData.value.map(x => ({ name: x.name, max: 100 }))
    radarValue.value = radarData.value.map(x => x.value)

    drawRadar()
  } catch (error) {
    console.error('加载电池单体详情失败:', error)
    // 可以在这里添加更多的错误处理逻辑，比如提示用户等
  }
}

function drawRadar() {
  const radarElement = document.getElementById('radar')
  if (!radarElement) {
    console.error('无法找到雷达图元素')
    return
  }

  const chart = echarts.init(radarElement)
  chart.setOption({
    radar: {
      indicator: radarIndicator.value
    },
    series: [{
      type: 'radar',
      data: [{ value: radarValue.value }]
    }]
  })
}

onMounted(load)
</script>

<style scoped>
.page { padding: 20px; }
</style>
