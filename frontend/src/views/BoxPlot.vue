<template>
  <div ref="chart" style="width: 100%; height: 300px"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ data: number[][] }>()

const chart = ref<HTMLDivElement>()

function render() {
  if (!chart.value) return
  const inst = echarts.init(chart.value)

  inst.setOption({
    tooltip: { trigger: 'item' },
    xAxis: { type: 'category', data: props.data.map((_, i) => `C${i}`) },
    yAxis: { type: 'value' },
    series: [{
      type: 'boxplot',
      data: props.data
    }]
  })
}

watch(() => props.data, render)
onMounted(render)
</script>
