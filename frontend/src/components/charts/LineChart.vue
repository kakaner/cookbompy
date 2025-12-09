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
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  LineController
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  LineController
)

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  datasets: {
    type: Array,
    default: null
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
  fill: {
    type: Boolean,
    default: false
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const chartData = () => {
  // If datasets prop is provided, use it (for multi-series charts)
  if (props.datasets && props.datasets.length > 0) {
    return {
      labels: props.datasets[0].data.map(item => item.label),
      datasets: props.datasets.map(dataset => ({
        label: dataset.label,
        data: dataset.data.map(item => item.value),
        borderColor: dataset.color || props.color,
        backgroundColor: dataset.fill ? `${dataset.color || props.color}40` : dataset.color || props.color,
        fill: dataset.fill || props.fill,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5
      }))
    }
  }
  
  // Single dataset (original behavior)
  return {
    labels: props.data.map(item => item.label),
    datasets: [
      {
        label: props.label,
        data: props.data.map(item => item.value),
        borderColor: props.color,
        backgroundColor: props.fill ? `${props.color}40` : props.color,
        fill: props.fill,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5
      }
    ]
  }
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: !!props.label,
      position: 'top'
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
      type: 'line',
      data: chartData(),
      options: chartOptions
    })
  }
})

watch(() => [props.data, props.datasets], () => {
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

