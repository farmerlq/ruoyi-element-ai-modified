<template>
  <div class="chart-test-container">
    <h1>ECharts 图表渲染测试</h1>
    
    <div class="test-section">
      <h2>1. 直接使用 ECharts API</h2>
      <div v-if="hasError1" class="error-message">{{ errorMessage1 }}</div>
      <div ref="directChartContainer" style="width: 100%; height: 400px;"></div>
    </div>
    
    <div class="test-section">
      <h2>2. 使用 chart-parser 工具函数</h2>
      <div v-if="hasError2" class="error-message">{{ errorMessage2 }}</div>
      <div ref="parserChartContainer" style="width: 100%; height: 400px;"></div>
    </div>
    
    <div class="test-section">
      <h2>3. 使用 EnhancedMarkdown 组件</h2>
      <div v-if="hasError3" class="error-message">{{ errorMessage3 }}</div>
      <EnhancedMarkdown :markdown="chartMarkdown" @error="handleMarkdownError" />
    </div>
    
    <div class="test-section">
      <h2>4. 初始尺寸为0的容器测试</h2>
      <div v-if="hasError4" class="error-message">{{ errorMessage4 }}</div>
      <div id="zeroSizeParent" :class="{expanded: isZeroSizeExpanded}" style="width: 0; height: 0; overflow: hidden; transition: width 1s ease, height 1s ease;">
        <div ref="zeroSizeChartContainer" style="width: 100%; height: 400px;"></div>
      </div>
      <button class="btn" @click="expandZeroSizeContainer" v-if="!isZeroSizeExpanded">展开容器</button>
    </div>
    
    <!-- 调试信息 -->
    <div class="debug-section">
      <h2>调试信息</h2>
      <div class="debug-info" v-for="(info, index) in debugInfo" :key="index">
        {{ info }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import * as echarts from 'echarts/core';
import EnhancedMarkdown from './EnhancedMarkdown/index.vue';
import { renderChart, destroyChart } from '@/utils/chart-parser';

// 状态变量
const directChartContainer = ref<HTMLElement | null>(null);
const parserChartContainer = ref<HTMLElement | null>(null);
const zeroSizeChartContainer = ref<HTMLElement | null>(null);
let directChart: any = null;
let zeroSizeChart: any = null;
const hasError1 = ref(false);
const hasError2 = ref(false);
const hasError3 = ref(false);
const hasError4 = ref(false);
const errorMessage1 = ref('');
const errorMessage2 = ref('');
const errorMessage3 = ref('');
const errorMessage4 = ref('');
const debugInfo = ref<string[]>([]);
const isZeroSizeExpanded = ref(false);

// 添加调试信息的函数
const addDebugInfo = (info: string) => {
  const timestamp = new Date().toLocaleTimeString();
  debugInfo.value.push(`[${timestamp}] ${info}`);
  console.log(`[${timestamp}] ${info}`);
  
  // 保持调试信息最多显示100条
  if (debugInfo.value.length > 100) {
    debugInfo.value.shift();
  }
};

// 检查容器是否在DOM中
const isInDOM = (element: HTMLElement | null): boolean => {
  if (!element) return false;
  try {
    return document.contains(element);
  } catch (e) {
    return false;
  }
};

// 安全地销毁图表实例
const safeDestroyChart = (chart: any, container?: HTMLElement | null) => {
  try {
    if (chart && typeof chart.dispose === 'function') {
      chart.dispose();
      addDebugInfo('图表实例已销毁');
    }
    if (container) {
      destroyChart(container);
    }
  } catch (error) {
    addDebugInfo('销毁图表实例时出错: ' + (error instanceof Error ? error.message : '未知错误'));
  }
};

// 测试用的图表配置
const chartOptions = {
  title: {
    text: '测试图表'
  },
  tooltip: {},
  xAxis: {
    type: 'category',
    data: ['一月', '二月', '三月', '四月', '五月', '六月']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110],
      type: 'bar'
    }
  ]
};

// 测试用的 Markdown 内容
const chartMarkdown = `# 图表示例

## 柱状图示例

\`\`\`echart
{
  "title": {
    "text": "月度销售额"
  },
  "xAxis": {
    "type": "category",
    "data": ["一月", "二月", "三月", "四月", "五月", "六月"]
  },
  "yAxis": {
    "type": "value"
  },
  "series": [
    {
      "data": [120, 200, 150, 80, 70, 110],
      "type": "bar"
    }
  ]
}
\`\`\``;

// 使用 ECharts API 直接渲染
const renderDirectChart = async () => {
  try {
    hasError1.value = false;
    errorMessage1.value = '';
    
    addDebugInfo('开始直接使用 ECharts API 渲染');
    
    // 确保 DOM 已经挂载
    await nextTick();
    
    if (!directChartContainer.value) {
      throw new Error('直接渲染图表容器不存在');
    }
    
    // 检查容器是否在DOM中
    if (!isInDOM(directChartContainer.value)) {
      addDebugInfo('警告：容器不在DOM中，添加延时重试');
      // 添加延时重试
      setTimeout(() => {
        if (isInDOM(directChartContainer.value)) {
          renderDirectChart();
        } else {
          hasError1.value = true;
          errorMessage1.value = '容器不在DOM中';
          addDebugInfo('重试失败，容器仍不在DOM中');
        }
      }, 500);
      return;
    }
    
    // 检查容器尺寸
    const rect = directChartContainer.value.getBoundingClientRect();
    addDebugInfo(`容器尺寸: 宽=${rect.width}, 高=${rect.height}`);
    
    // 初始化图表实例
    directChart = echarts.init(directChartContainer.value, undefined, { 
      renderer: 'svg' // 使用 SVG 渲染器以获得更好的兼容性
    });
    addDebugInfo('图表实例初始化成功，准备设置配置');
    
    directChart.setOption(chartOptions);
    addDebugInfo('配置设置成功，图表已渲染');
    
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize);
    
    // 处理容器尺寸为0的情况
    if (rect.width === 0 || rect.height === 0) {
      addDebugInfo('容器尺寸为0，添加尺寸变化监听');
      const resizeObserver = new ResizeObserver(entries => {
        const entry = entries[0];
        if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
          if (directChart && !directChart.isDisposed()) {
            directChart.resize();
            directChart.setOption(chartOptions, true);
            addDebugInfo('图表因尺寸变化重新渲染');
          }
          resizeObserver.unobserve(directChartContainer.value!);
        }
      });
      resizeObserver.observe(directChartContainer.value);
    }
    
    // 延时重新渲染，确保图表正确显示
    setTimeout(() => {
      if (directChart && !directChart.isDisposed()) {
        directChart.resize();
        directChart.setOption(chartOptions, true);
        addDebugInfo('图表二次渲染完成');
      }
    }, 100);
    
  } catch (error) {
    hasError1.value = true;
    errorMessage1.value = error instanceof Error ? error.message : '未知错误';
    addDebugInfo('直接使用 ECharts API 渲染失败: ' + errorMessage1.value);
    console.error('直接使用 ECharts API 渲染失败:', error);
  }
};

// 使用 chart-parser 渲染
const renderWithParser = async () => {
  try {
    hasError2.value = false;
    errorMessage2.value = '';
    
    addDebugInfo('开始使用 chart-parser 渲染');
    
    // 确保 DOM 已经挂载
    await nextTick();
    
    if (!parserChartContainer.value) {
      throw new Error('parser 渲染图表容器不存在');
    }
    
    // 检查容器是否在DOM中
    if (!isInDOM(parserChartContainer.value)) {
      addDebugInfo('警告：chart-parser 容器不在DOM中，添加延时重试');
      // 添加延时重试
      setTimeout(() => {
        if (isInDOM(parserChartContainer.value)) {
          renderWithParser();
        } else {
          hasError2.value = true;
          errorMessage2.value = '容器不在DOM中';
          addDebugInfo('重试失败，容器仍不在DOM中');
        }
      }, 500);
      return;
    }
    
    // 检查容器尺寸
    const rect = parserChartContainer.value.getBoundingClientRect();
    addDebugInfo(`chart-parser 容器尺寸: 宽=${rect.width}, 高=${rect.height}`);
    
    // 创建图表配置对象
    const chartConfig = {
      type: 'echart' as const,
      options: chartOptions
    };
    
    addDebugInfo('开始调用 renderChart 函数');
    renderChart(parserChartContainer.value, chartConfig);
    addDebugInfo('使用 chart-parser 渲染成功');
    
  } catch (error) {
    hasError2.value = true;
    errorMessage2.value = error instanceof Error ? error.message : '未知错误';
    addDebugInfo('使用 chart-parser 渲染失败: ' + errorMessage2.value);
    console.error('使用 chart-parser 渲染失败:', error);
  }
};

// 渲染初始尺寸为0的容器中的图表
const renderZeroSizeChart = async () => {
  try {
    hasError4.value = false;
    errorMessage4.value = '';
    
    addDebugInfo('开始渲染初始尺寸为0的容器中的图表');
    
    // 确保 DOM 已经挂载
    await nextTick();
    
    if (!zeroSizeChartContainer.value) {
      throw new Error('零尺寸容器不存在');
    }
    
    // 检查容器是否在DOM中
    if (!isInDOM(zeroSizeChartContainer.value)) {
      addDebugInfo('警告：零尺寸容器不在DOM中');
      hasError4.value = true;
      errorMessage4.value = '容器不在DOM中';
      return;
    }
    
    // 检查容器尺寸 (预期为0)
    const rect = zeroSizeChartContainer.value.getBoundingClientRect();
    addDebugInfo(`零尺寸容器初始尺寸: 宽=${rect.width}, 高=${rect.height}`);
    
    // 创建图表配置对象
    const chartConfig = {
      type: 'echart' as const,
      options: chartOptions
    };
    
    addDebugInfo('调用 renderChart 函数处理零尺寸容器');
    renderChart(zeroSizeChartContainer.value, chartConfig);
    addDebugInfo('零尺寸容器图表渲染尝试完成');
    
    // 监听展开事件，在容器展开后刷新图表
    watch(isZeroSizeExpanded, (newVal) => {
      if (newVal && zeroSizeChartContainer.value) {
        addDebugInfo('零尺寸容器已展开，等待动画完成后刷新图表');
        setTimeout(() => {
          const newRect = zeroSizeChartContainer.value!.getBoundingClientRect();
          addDebugInfo(`展开后的容器尺寸: 宽=${newRect.width}, 高=${newRect.height}`);
          
          // 重新调用 renderChart 确保图表正确渲染
          renderChart(zeroSizeChartContainer.value!, chartConfig);
          addDebugInfo('零尺寸容器展开后图表重新渲染完成');
        }, 1000); // 等待展开动画完成
      }
    });
    
  } catch (error) {
    hasError4.value = true;
    errorMessage4.value = error instanceof Error ? error.message : '未知错误';
    addDebugInfo('零尺寸容器图表渲染失败: ' + errorMessage4.value);
    console.error('零尺寸容器图表渲染失败:', error);
  }
};

// 展开零尺寸容器
const expandZeroSizeContainer = () => {
  addDebugInfo('点击展开零尺寸容器');
  isZeroSizeExpanded.value = true;
};

// 处理窗口大小变化
const handleResize = () => {
  if (directChart) {
    directChart.resize();
    addDebugInfo('图表已响应窗口大小变化');
  }
};

// 增强 Markdown 组件的错误处理
const handleMarkdownError = (error: any) => {
  hasError3.value = true;
  errorMessage3.value = error instanceof Error ? error.message : '未知错误';
  addDebugInfo(`EnhancedMarkdown 组件错误: ${errorMessage3.value}`);
};

// 组件挂载时渲染图表
onMounted(() => {
  addDebugInfo('ChartTest 组件已挂载');
  
  // 延迟渲染，确保 DOM 已完全更新
  setTimeout(() => {
    addDebugInfo('开始渲染测试图表');
    renderDirectChart();
    renderWithParser();
    renderZeroSizeChart();
  }, 500);
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
});

// 组件卸载时清理
onUnmounted(() => {
  addDebugInfo('ChartTest 组件即将卸载');
  
  // 安全销毁图表实例
  safeDestroyChart(directChart);
  
  // 清理 parserChartContainer 中的图表
  if (parserChartContainer.value) {
    destroyChart(parserChartContainer.value);
  }
  
  // 清理 zeroSizeChartContainer 中的图表
  if (zeroSizeChartContainer.value) {
    destroyChart(zeroSizeChartContainer.value);
  }
  
  // 移除事件监听器
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.chart-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.error-message {
  color: #f56c6c;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
}

.debug-section {
  margin-top: 40px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #f5f5f5;
  max-height: 300px;
  overflow-y: auto;
}

.debug-info {
  font-family: monospace;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}

h1 {
  color: #1e293b;
  margin-bottom: 30px;
}

h2 {
  color: #334155;
  margin-bottom: 20px;
}
</style>