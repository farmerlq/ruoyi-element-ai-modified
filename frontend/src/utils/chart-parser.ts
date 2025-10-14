/**
 * 图表解析器
 * 用于解析和渲染各种图表，包括 ECharts 图表
 */

// ECharts 核心模块
import * as echarts from 'echarts/core';
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  TreeChart,
  TreemapChart,
  GraphChart,
  GaugeChart,
  FunnelChart,
  ParallelChart,
  SankeyChart,
  BoxplotChart,
  CandlestickChart,
  EffectScatterChart,
  LinesChart,
  HeatmapChart,
  PictorialBarChart,
  ThemeRiverChart,
  SunburstChart,
  CustomChart,
} from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  PolarComponent,
  AxisPointerComponent,
  LegendComponent,
  DataZoomComponent,
  VisualMapComponent,
  TimelineComponent,
  CalendarComponent,
  GraphicComponent,
  ToolboxComponent,
  DatasetComponent,
  TransformComponent,
  AriaComponent,
  ParallelComponent,
  LegendScrollComponent,
  LegendPlainComponent,
  GridSimpleComponent,
  BrushComponent,
  MarkPointComponent,
  MarkLineComponent,
  MarkAreaComponent,
  SingleAxisComponent,
} from 'echarts/components';
import { SVGRenderer, CanvasRenderer } from 'echarts/renderers';

// 注册 ECharts 组件
echarts.use([
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  TreeChart,
  TreemapChart,
  GraphChart,
  GaugeChart,
  FunnelChart,
  ParallelChart,
  SankeyChart,
  BoxplotChart,
  CandlestickChart,
  EffectScatterChart,
  LinesChart,
  HeatmapChart,
  PictorialBarChart,
  ThemeRiverChart,
  SunburstChart,
  CustomChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  PolarComponent,
  AxisPointerComponent,
  LegendComponent,
  DataZoomComponent,
  VisualMapComponent,
  TimelineComponent,
  CalendarComponent,
  GraphicComponent,
  ToolboxComponent,
  DatasetComponent,
  TransformComponent,
  AriaComponent,
  ParallelComponent,
  LegendScrollComponent,
  LegendPlainComponent,
  GridSimpleComponent,
  BrushComponent,
  MarkPointComponent,
  MarkLineComponent,
  MarkAreaComponent,
  SingleAxisComponent,
  SVGRenderer,
  CanvasRenderer,
]);

export interface ChartConfig {
  type: 'echart' | 'mermaid' | 'chart';
  options: any;
  data?: any;
}

/**
 * 解析图表代码块
 * @param code 图表代码块内容
 * @param lang 代码块语言类型
 * @returns 解析后的图表配置
 */
export function parseChartCodeBlock(code: string, lang: string): ChartConfig | null {
  try {
    console.log('解析图表代码块:', { code, lang });
    // 处理 ECharts 图表
    if (lang === 'echart' || lang === 'echarts') {
      // 尝试解析为 JSON
      const options = JSON.parse(code);
      console.log('ECharts 配置解析成功:', options);
      return {
        type: 'echart',
        options,
      };
    }
    
    // 处理通用 chart 图表
    if (lang === 'chart') {
      // 尝试解析为 JSON
      const options = JSON.parse(code);
      return {
        type: 'echart',
        options,
      };
    }
    
    // 处理 Mermaid 图表
    if (lang === 'mermaid') {
      return {
        type: 'mermaid',
        options: code,
      };
    }
    
    console.log('不支持的图表语言类型:', lang);
    return null;
  } catch (error) {
    console.error('图表解析错误:', error);
    return null;
  }
}

/**
 * 渲染图表到指定容器
 * @param container 容器元素
 * @param config 图表配置
 */
export function renderChart(container: HTMLElement, config: ChartConfig): void {
  try {
    console.log('开始渲染图表:', { container, config });
    
    // 检查容器是否有效
    if (!container) {
      console.error('图表容器不存在');
      return;
    }
    
    // 检查容器是否已添加到DOM
    if (!document.contains(container)) {
      console.warn('图表容器尚未添加到DOM中');
      // 添加延时重试
      setTimeout(() => {
        if (document.contains(container)) {
          renderChart(container, config);
        } else {
          console.error('重试失败，容器仍未添加到DOM');
          container.innerHTML = '<div class="chart-error">图表容器未找到</div>';
        }
      }, 500);
      return;
    }
    
    // 检查容器尺寸
    const rect = container.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      console.warn('容器尺寸为0，添加延时重试');
      // 添加延时重试
      setTimeout(() => {
        const newRect = container.getBoundingClientRect();
        if (newRect.width > 0 && newRect.height > 0) {
          renderChart(container, config);
        } else {
          console.error('重试失败，容器尺寸仍为0');
          container.innerHTML = '<div class="chart-error">图表容器尺寸无效</div>';
        }
      }, 500);
      return;
    }
    
    // 清空容器
    container.innerHTML = '';
    
    switch (config.type) {
      case 'echart':
        // 创建 ECharts 图表
        console.log('准备创建 ECharts 图表');
        const chart = createECharts(container, config.options);
        if (chart) {
          container.setAttribute('data-chart-type', 'echart');
          console.log('ECharts 图表渲染成功');
        } else {
          container.innerHTML = '<div class="chart-error">图表渲染失败</div>';
          console.log('ECharts 图表渲染失败');
        }
        break;
        
      case 'mermaid':
        // Mermaid 图表将在 Markdown 渲染器中处理
        container.setAttribute('data-chart-type', 'mermaid');
        container.setAttribute('data-mermaid-code', config.options);
        container.innerHTML = '<div class="chart-placeholder">Mermaid 图表加载中...</div>';
        console.log('Mermaid 图表渲染完成');
        break;
        
      default:
        console.warn('不支持的图表类型:', config.type);
        container.innerHTML = '<div class="chart-error">不支持的图表类型</div>';
        break;
    }
  } catch (error) {
    console.error('图表渲染错误:', error);
    if (container) {
      container.innerHTML = `<div class="chart-error">图表渲染失败: ${error instanceof Error ? error.message : '未知错误'}</div>`;
    }
  }
}

/**
 * 创建 ECharts 实例
 * @param container 容器元素
 * @param options 图表配置
 * @returns ECharts 实例
 */
export function createECharts(container: HTMLElement, options: any): any {
  try {
    console.log('初始化 ECharts 实例:', { container, options });
    // 检查容器是否有效
    if (!container) {
      console.error('ECharts 容器不存在');
      return null;
    }
    
    // 检查容器是否已添加到DOM
    if (!document.contains(container)) {
      console.warn('ECharts 容器尚未添加到DOM中');
    }
    
    // 检查容器的尺寸
    const containerRect = container.getBoundingClientRect();
    console.log('容器尺寸:', containerRect);
    
    // 初始化图表实例
    const chart = echarts.init(container, undefined, { 
      renderer: 'svg' // 使用 SVG 渲染器以获得更好的兼容性
    });
    console.log('ECharts 实例创建成功:', chart);
    
    // 设置图表选项
    chart.setOption(options, true);
    console.log('ECharts 配置设置完成');
    
    // 监听窗口大小变化，自适应图表
    const resizeObserver = new ResizeObserver(() => {
      if (chart && !chart.isDisposed()) {
        chart.resize();
        console.log('ECharts 图表已调整大小');
      }
    });
    resizeObserver.observe(container);
    
    // 处理容器尺寸为0的情况
    if (containerRect.width === 0 || containerRect.height === 0) {
      console.warn('容器尺寸为0，添加尺寸变化监听');
      // 添加一个尺寸监听器，当尺寸变化时重新渲染
      const sizeObserver = new ResizeObserver(entries => {
        const entry = entries[0];
        if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
          if (chart && !chart.isDisposed()) {
            chart.resize();
            chart.setOption(options, true);
            console.log('ECharts 图表因尺寸变化重新渲染');
          }
          sizeObserver.unobserve(container);
        }
      });
      sizeObserver.observe(container);
    }
    
    // 添加一个延时重新渲染，确保图表正确显示
    setTimeout(() => {
      if (chart && !chart.isDisposed()) {
        chart.resize();
        chart.setOption(options, true);
        console.log('ECharts 图表二次渲染完成');
      }
    }, 100);
    
    return chart;
  } catch (error) {
    console.error('ECharts 创建失败:', error);
    return null;
  }
}

/**
 * 销毁图表实例
 * @param container 容器元素
 */
export function destroyChart(container: HTMLElement): void {
  try {
    const chartType = container.getAttribute('data-chart-type');
    
    if (chartType === 'echart') {
      const chart = echarts.getInstanceByDom(container);
      if (chart) {
        chart.dispose();
      }
    }
    
    container.removeAttribute('data-chart-type');
    container.removeAttribute('data-mermaid-code');
  } catch (error) {
    console.error('图表销毁错误:', error);
  }
}

export default {
  parseChartCodeBlock,
  createECharts,
  renderChart,
  destroyChart,
};