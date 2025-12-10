<template>
  <div class="page">
    <h2>电池簇详情（Rack {{ rackId }}）</h2>

    <TimeseriesChart
      title="簇级 V / I / SOC"
      :series="series" />

    <h3 style="margin-top: 20px">电压热力图</h3>
    <Heatmap :matrix="volMatrix" />

    <h3 style="margin-top: 20px">温度热力图</h3>
    <Heatmap :matrix="tempMatrix" />

    <h3 style="margin-top: 20px">箱线图</h3>
    <BoxPlot :data="boxData" />

    <h3 style="margin-top: 20px">异常电芯</h3>
    <a-list bordered>
      <a-list-item v-for="c in abnormalCells" :key="c">{{ c }}</a-list-item>
    </a-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getRackDetail } from '@/api'
import Heatmap from './Heatmap.vue'
import TimeseriesChart from './TimeseriesChart.vue'
import BoxPlot from './BoxPlot.vue'

const route = useRoute()
const rackId = route.params.id

const series = ref<any[]>([])
const volMatrix = ref<number[][]>([])
const tempMatrix = ref<number[][]>([])
const boxData = ref<any[]>([])
const abnormalCells = ref<string[]>([])

async function load() {
  const r = await api.getRackDetail(rackId)
  series.value = r.timeseries
  volMatrix.value = r.vol_matrix
  tempMatrix.value = r.temp_matrix
  boxData.value = r.boxplot
  abnormalCells.value = r.abnormal
}

onMounted(load)
</script>

<style scoped>
.page { padding: 20px; }
</style>
