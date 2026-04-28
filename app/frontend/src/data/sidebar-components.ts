import {
  BadgeDollarSign,
  Bot,
  Brain,
  Calculator,
  ChartLine,
  ChartPie,
  LucideIcon,
  Network,
  Play,
  Zap
} from 'lucide-react';
import { Agent, getAgents } from './agents';

export interface ComponentItem {
  name: string;
  icon: LucideIcon;
}

export interface ComponentGroup {
  name: string;
  icon: LucideIcon;
  iconColor: string;
  items: ComponentItem[];
}

export const getComponentGroups = async (): Promise<ComponentGroup[]> => {
  const agents = await getAgents();
  
  return [
    {
      name: "开始节点",
      icon: Play,
      iconColor: "text-blue-500",
      items: [
        { name: "投资组合输入", icon: ChartPie },
        { name: "股票输入", icon: ChartLine },
      ]
    },
    {
      name: "分析师",
      icon: Bot,
      iconColor: "text-red-500",
      items: agents.map((agent: Agent) => ({
        name: agent.display_name,
        icon: Bot
      }))
    },
    {
      name: "智能体群",
      icon: Network,
      iconColor: "text-yellow-500",
      items: [
        { name: "数据精灵", icon: Calculator },
        { name: "市场先锋", icon: Zap },
        { name: "价值投资者", icon: BadgeDollarSign },
      ]
    },
    {
      name: "结束节点",
      icon: Brain,
      iconColor: "text-green-500",
      items: [
        { name: "投资组合管理", icon: Brain },
      ]
    },
  ];
};
