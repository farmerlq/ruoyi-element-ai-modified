# 图表示例

以下是一些可以在聊天中使用的图表示例：

## 柱状图示例

```echart
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
```

## 折线图示例

```chart
{
  "title": {
    "text": "用户访问趋势"
  },
  "xAxis": {
    "type": "category",
    "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
  },
  "yAxis": {
    "type": "value"
  },
  "series": [
    {
      "data": [120, 132, 101, 134, 90, 230, 210],
      "type": "line"
    }
  ]
}
```

## 饼图示例

```echarts
{
  "title": {
    "text": "浏览器市场份额",
    "left": "center"
  },
  "tooltip": {
    "trigger": "item"
  },
  "legend": {
    "orient": "vertical",
    "left": "left"
  },
  "series": [
    {
      "name": "访问来源",
      "type": "pie",
      "radius": "50%",
      "data": [
        { "value": 1048, "name": "Chrome" },
        { "value": 735, "name": "Edge" },
        { "value": 580, "name": "Firefox" },
        { "value": 484, "name": "Safari" },
        { "value": 300, "name": "Opera" }
      ],
      "emphasis": {
        "itemStyle": {
          "shadowBlur": 10,
          "shadowOffsetX": 0,
          "shadowColor": "rgba(0, 0, 0, 0.5)"
        }
      }
    }
  ]
}
```