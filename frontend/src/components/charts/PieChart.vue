<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  PieController
} from 'chart.js'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  PieController
)

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  },
  colors: {
    type: Array,
    default: () => [
      '#9B4819',
      '#6B7456',
      '#D4AF37',
      '#8B7355',
      '#A67C52',
      '#C9A961',
      '#E8D5B7',
      '#F0EDE8'
    ]
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const chartData = () => {
  const labels = props.data.map(item => {
    const label = item.label || item.name || item.genre || item.book_type || item.format
    const icon = item.icon || ''
    return icon ? `${icon} ${label}` : label
  })
  
  return {
    labels: labels,
    datasets: [
      {
        data: props.data.map(item => item.value || item.count || item.percentage),
        backgroundColor: props.colors,
        borderColor: '#F8F5F0',
        borderWidth: 2
      }
    ]
  }
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        font: {
          family: 'Inter, sans-serif',
          size: 12
        },
        color: '#2C2C2C',
        padding: 15,
        usePointStyle: true
      }
    },
    title: {
      display: !!props.title,
      text: props.title,
      font: {
        family: 'Crimson Text, serif',
        size: 16,
        weight: '600'
      },
      color: '#2C2C2C'
    },
    tooltip: {
      backgroundColor: 'rgba(44, 44, 44, 0.9)',
      titleFont: {
        family: 'Inter, sans-serif'
      },
      bodyFont: {
        family: 'Inter, sans-serif'
      },
      padding: 12,
      cornerRadius: 6,
      callbacks: {
        label: function(context) {
          const label = context.label || ''
          const value = context.parsed || 0
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  }
}

onMounted(() => {
  if (chartCanvas.value) {
    chartInstance = new ChartJS(chartCanvas.value, {
      type: 'pie',
      data: chartData(),
      options: chartOptions
    })
  }
})

watch(() => props.data, () => {
  if (chartInstance) {
    chartInstance.data = chartData()
    chartInstance.update()
  }
}, { deep: true })

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>

