<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  BarController
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  BarController
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
  label: {
    type: String,
    default: 'Value'
  },
  color: {
    type: String,
    default: '#9B4819'
  },
  horizontal: {
    type: Boolean,
    default: false
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const chartData = () => {
  return {
    labels: props.data.map(item => item.label || item.name || item.genre || item.book_type || item.format),
    datasets: [
      {
        label: props.label,
        data: props.data.map(item => item.value || item.count || item.percentage),
        backgroundColor: props.color,
        borderColor: props.color,
        borderWidth: 1
      }
    ]
  }
}

const chartOptions = {
  indexAxis: props.horizontal ? 'y' : 'x',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
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
      cornerRadius: 6
    }
  },
  scales: {
    x: {
      ticks: {
        font: {
          family: 'Inter, sans-serif',
          size: 11
        },
        color: '#6B7456'
      },
      grid: {
        color: 'rgba(107, 116, 86, 0.1)'
      }
    },
    y: {
      ticks: {
        font: {
          family: 'Inter, sans-serif',
          size: 11
        },
        color: '#6B7456'
      },
      grid: {
        color: 'rgba(107, 116, 86, 0.1)'
      },
      beginAtZero: true
    }
  }
}

onMounted(() => {
  if (chartCanvas.value) {
    chartInstance = new ChartJS(chartCanvas.value, {
      type: 'bar',
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

