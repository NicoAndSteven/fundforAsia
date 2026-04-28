export interface MultiNodeDefinition {
  name: string;
  nodes: {
    componentName: string;
    offsetX: number;
    offsetY: number;
  }[];
  edges: {
    source: string;
    target: string;
  }[];
}

const multiNodeDefinition: Record<string, MultiNodeDefinition> = {
  "价值投资者": {
    name: "价值投资者",
    nodes: [
      { componentName: "股票输入", offsetX: 0, offsetY: 0 },
      { componentName: "本杰明·格雷厄姆", offsetX: 400, offsetY: -400 },
      { componentName: "查理·芒格", offsetX: 400, offsetY: 0 },
      { componentName: "沃伦·巴菲特", offsetX: 400, offsetY: 400 },
      { componentName: "投资组合管理", offsetX: 800, offsetY: 0 },
    ],
    edges: [
      { source: "股票输入", target: "本杰明·格雷厄姆" },
      { source: "股票输入", target: "查理·芒格" },
      { source: "股票输入", target: "沃伦·巴菲特" },
      { source: "本杰明·格雷厄姆", target: "投资组合管理" },
      { source: "查理·芒格", target: "投资组合管理" },
      { source: "沃伦·巴菲特", target: "投资组合管理" },
    ],
  },
  "数据精灵": {
    name: "数据精灵",
    nodes: [
      { componentName: "股票输入", offsetX: 0, offsetY: 0 },
      { componentName: "技术分析师", offsetX: 400, offsetY: -550 },
      { componentName: "基本面分析师", offsetX: 400, offsetY: -200 },
      { componentName: "情绪分析师", offsetX: 400, offsetY: 150 },
      { componentName: "估值分析师", offsetX: 400, offsetY: 500 },
      { componentName: "投资组合管理", offsetX: 800, offsetY: 0 },
    ],
    edges: [
      { source: "股票输入", target: "技术分析师" },
      { source: "股票输入", target: "基本面分析师" },
      { source: "股票输入", target: "情绪分析师" },
      { source: "股票输入", target: "估值分析师" },
      { source: "技术分析师", target: "投资组合管理" },
      { source: "基本面分析师", target: "投资组合管理" },
      { source: "情绪分析师", target: "投资组合管理" },
      { source: "估值分析师", target: "投资组合管理" },
    ],
  },
  "市场先锋": {
    name: "市场先锋",
    nodes: [
      { componentName: "股票输入", offsetX: 0, offsetY: 0 },
      { componentName: "迈克尔·布瑞", offsetX: 400, offsetY: -400 },
      { componentName: "比尔·阿克曼", offsetX: 400, offsetY: 0 },
      { componentName: "斯坦利·德鲁肯米勒", offsetX: 400, offsetY: 400 },
      { componentName: "投资组合管理", offsetX: 800, offsetY: 0 },
    ],
    edges: [
      { source: "股票输入", target: "迈克尔·布瑞" },
      { source: "股票输入", target: "比尔·阿克曼" },
      { source: "股票输入", target: "斯坦利·德鲁肯米勒" },
      { source: "迈克尔·布瑞", target: "投资组合管理" },
      { source: "比尔·阿克曼", target: "投资组合管理" },
      { source: "斯坦利·德鲁肯米勒", target: "投资组合管理" },
    ],
  },
  // 保留英文名称映射以兼容旧数据
  "Value Investors": {
    name: "价值投资者",
    nodes: [
      { componentName: "股票输入", offsetX: 0, offsetY: 0 },
      { componentName: "本杰明·格雷厄姆", offsetX: 400, offsetY: -400 },
      { componentName: "查理·芒格", offsetX: 400, offsetY: 0 },
      { componentName: "沃伦·巴菲特", offsetX: 400, offsetY: 400 },
      { componentName: "投资组合管理", offsetX: 800, offsetY: 0 },
    ],
    edges: [
      { source: "股票输入", target: "本杰明·格雷厄姆" },
      { source: "股票输入", target: "查理·芒格" },
      { source: "股票输入", target: "沃伦·巴菲特" },
      { source: "本杰明·格雷厄姆", target: "投资组合管理" },
      { source: "查理·芒格", target: "投资组合管理" },
      { source: "沃伦·巴菲特", target: "投资组合管理" },
    ],
  },
  "Data Wizards": {
    name: "数据精灵",
    nodes: [
      { componentName: "股票输入", offsetX: 0, offsetY: 0 },
      { componentName: "技术分析师", offsetX: 400, offsetY: -550 },
      { componentName: "基本面分析师", offsetX: 400, offsetY: -200 },
      { componentName: "情绪分析师", offsetX: 400, offsetY: 150 },
      { componentName: "估值分析师", offsetX: 400, offsetY: 500 },
      { componentName: "投资组合管理", offsetX: 800, offsetY: 0 },
    ],
    edges: [
      { source: "股票输入", target: "技术分析师" },
      { source: "股票输入", target: "基本面分析师" },
      { source: "股票输入", target: "情绪分析师" },
      { source: "股票输入", target: "估值分析师" },
      { source: "技术分析师", target: "投资组合管理" },
      { source: "基本面分析师", target: "投资组合管理" },
      { source: "情绪分析师", target: "投资组合管理" },
      { source: "估值分析师", target: "投资组合管理" },
    ],
  },
  "Market Mavericks": {
    name: "市场先锋",
    nodes: [
      { componentName: "股票输入", offsetX: 0, offsetY: 0 },
      { componentName: "迈克尔·布瑞", offsetX: 400, offsetY: -400 },
      { componentName: "比尔·阿克曼", offsetX: 400, offsetY: 0 },
      { componentName: "斯坦利·德鲁肯米勒", offsetX: 400, offsetY: 400 },
      { componentName: "投资组合管理", offsetX: 800, offsetY: 0 },
    ],
    edges: [
      { source: "股票输入", target: "迈克尔·布瑞" },
      { source: "股票输入", target: "比尔·阿克曼" },
      { source: "股票输入", target: "斯坦利·德鲁肯米勒" },
      { source: "迈克尔·布瑞", target: "投资组合管理" },
      { source: "比尔·阿克曼", target: "投资组合管理" },
      { source: "斯坦利·德鲁肯米勒", target: "投资组合管理" },
    ],
  },
};

export function getMultiNodeDefinition(name: string): MultiNodeDefinition | null {
  return multiNodeDefinition[name] || null;
}

export function isMultiNodeComponent(componentName: string): boolean {
  return componentName in multiNodeDefinition;
} 