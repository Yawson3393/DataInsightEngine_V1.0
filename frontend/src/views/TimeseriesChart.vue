<template>
  <div ref="chart" style="width: 100%; height: 300px"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ title?: string; series: any[] }>()

const chart = ref<HTMLDivElement>()

function render() {
  if (!chart.value) return
  const inst = echarts.init(chart.value)

  inst.setOption({
    title: { text: props.title },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time' },
    yAxis: { type: 'value' },
    series: props.series
  })
}

watch(() => props.series, render)
onMounted(render)
</script>
