<template>
  <div ref="chart" style="width: 100%; height: 300px"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ matrix: number[][] }>()

const chart = ref<HTMLDivElement>()

function render() {
  if (!chart.value) return
  const inst = echarts.init(chart.value)

  const rows = props.matrix.length
  const cols = props.matrix[0]?.length || 0

  const data = []
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      data.push([c, r, props.matrix[r][c]])
    }
  }

  inst.setOption({
    tooltip: {},
    visualMap: { min: 0, max: 5000, calculable: true },
    xAxis: { type: 'category' },
    yAxis: { type: 'category' },
    series: [{
      type: 'heatmap',
      data,
      emphasis: { itemStyle: { borderColor: '#333' } }
    }]
  })
}

watch(() => props.matrix, render)
onMounted(render)
</script>
