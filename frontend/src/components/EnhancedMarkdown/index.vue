<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { XMarkdown } from 'vue-element-plus-x';
import { parseChartCodeBlock, renderChart, destroyChart } from '@/utils/chart-parser';

const props = defineProps<{
  markdown: string;
  themes?: Record<string, string>;
  defaultThemeMode?: 'light' | 'dark';
}>();

const markdownContainer = ref<HTMLElement | null>(null);
const chartPlaceholders = ref<Array<{id: string, config: any}>>([]);
const renderedCharts = ref<Set<string>>(new Set());
const markdownKey = ref(0); // 用于强制重新渲染 XMarkdown 组件

// 生成唯一ID的函数
const generateUniqueId = () => {
  return `chart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// 处理 Markdown 内容，识别并替换图表代码块
const processedMarkdown = computed(() => {
  if (!props.markdown) return '';
  
  // 清空图表占位符数组
  chartPlaceholders.value = [];
  
  console.log('处理Markdown内容:', props.markdown);
  
  // 查找代码块并替换为占位符
  const result = props.markdown.replace(/```(\w+)[\s\S]*?```/g, (match) => {
    console.log('匹配到代码块:', match);
    // 提取语言和代码内容
    const langMatch = match.match(/```(\w+)\s*\n([\s\S]*)\n?```/);
    if (!langMatch) {
      console.log('无法解析代码块格式');
      return match;
    }
    
    const lang = langMatch[1];
    const code = langMatch[2];
    
    console.log('代码块语言:', lang);
    console.log('代码块内容:', code);
    
    const trimmedCode = code.trim();
    const chartConfig = parseChartCodeBlock(trimmedCode, lang);
    
    if (chartConfig) {
      // 生成唯一标识符
      const chartId = generateUniqueId();
      // 保存占位符信息
      chartPlaceholders.value.push({
        id: chartId,
        config: chartConfig
      });
      console.log('生成图表配置:', { id: chartId, lang, hasConfig: !!chartConfig });
      // 返回空字符串，完全移除代码块，避免任何占位符元素
      return '';
    }
    
    // 非图表代码块保持原样
    return match;
  });
  
  console.log('处理后的Markdown内容:', result);
  console.log('图表配置列表:', chartPlaceholders.value);
  
  return result;
});

// Markdown 渲染完成后的回调
const onMarkdownRendered = () => {
  console.log('Markdown渲染完成，开始渲染图表');
  console.log('图表配置列表:', chartPlaceholders.value);
  // 立即渲染图表
  renderChartsDirectly();
};

// 直接在容器中渲染图表（不依赖占位符）
const renderChartsDirectly = () => {
  if (!markdownContainer.value) {
    console.log('Markdown容器不存在');
    return;
  }
  
  const container = markdownContainer.value;
  
  // 移除之前添加的图表容器
  const oldChartsDirectContainer = container.querySelector('.charts-direct-container');
  if (oldChartsDirectContainer) {
    oldChartsDirectContainer.remove();
  }
  
  // 如果没有图表需要渲染，直接返回
  if (chartPlaceholders.value.length === 0) {
    console.log('没有图表需要渲染');
    return;
  }
  
  // 创建一个包装容器来放置所有图表
  const chartsDirectContainer = document.createElement('div');
  chartsDirectContainer.className = 'charts-direct-container';
  container.appendChild(chartsDirectContainer);
  
  // 遍历所有图表配置
  chartPlaceholders.value.forEach(({config}, index) => {
    try {
      // 创建图表容器
      const chartContainer = document.createElement('div');
      chartContainer.className = 'chart-container';
      chartContainer.style.width = '100%';
      chartContainer.style.height = '400px';
      chartContainer.style.margin = '16px 0';
      
      // 添加到图表容器中
      chartsDirectContainer.appendChild(chartContainer);
      
      // 延迟渲染图表，确保容器已添加到DOM
      setTimeout(() => {
        console.log('渲染图表:', { index, config });
        if (document.contains(chartContainer)) {
          renderChart(chartContainer, config);
        } else {
          console.log('图表容器未添加到DOM中');
        }
      }, 0);
      
    } catch (error) {
      console.error('图表渲染失败:', error);
      // 显示错误信息
      const errorElement = document.createElement('div');
      errorElement.className = 'chart-error';
      errorElement.textContent = '图表渲染失败: ' + (error instanceof Error ? error.message : String(error));
      errorElement.style.padding = '20px';
      errorElement.style.backgroundColor = '#fef2f2';
      errorElement.style.border = '1px solid #fecaca';
      errorElement.style.borderRadius = '8px';
      errorElement.style.color = '#dc2626';
      errorElement.style.margin = '16px 0';
      chartsDirectContainer.appendChild(errorElement);
    }
  });
};

// 添加手动渲染方法
const forceRenderCharts = () => {
  console.log('手动强制渲染图表');
  renderChartsDirectly();
};

// 销毁图表实例
const destroyCharts = () => {
  if (!markdownContainer.value) return;
  
  const chartContainers = markdownContainer.value.querySelectorAll('.chart-container');
  chartContainers.forEach(container => {
    destroyChart(container as HTMLElement);
  });
  
  // 移除直接添加的图表容器
  const chartsDirectContainer = markdownContainer.value.querySelector('.charts-direct-container');
  if (chartsDirectContainer) {
    chartsDirectContainer.remove();
  }
  
  renderedCharts.value.clear();
};

// 暴露方法
defineExpose({
  refresh: () => {
    destroyCharts();
  },
  forceRenderCharts
});

// 监听 markdown 属性变化
watch(
  () => props.markdown,
  (newMarkdown, oldMarkdown) => {
    console.log('Markdown内容发生变化', { newMarkdown, oldMarkdown });
    // 总是更新 key 值强制 XMarkdown 重新渲染，确保实时内容正确显示
    markdownKey.value = Date.now();
    // 销毁旧图表
    destroyCharts();
    // 重新渲染
    nextTick(() => {
      setTimeout(() => {
        renderChartsDirectly();
      }, 0);
    });
  },
  { immediate: true }
);

// 组件卸载前销毁图表
onUnmounted(() => {
  destroyCharts();
});
</script>

<template>
  <div ref="markdownContainer" class="enhanced-markdown">
    <XMarkdown
      :key="markdownKey"
      :markdown="processedMarkdown"
      :themes="themes"
      :default-theme-mode="defaultThemeMode"
      class="markdown-content"
      @rendered="onMarkdownRendered"
    />
  </div>
</template>
