import { AppNode } from "@/nodes/types";
import { Agent, getAgents } from "./agents";

// Map of sidebar item names to node creation functions
export interface NodeTypeDefinition {
  createNode: (position: { x: number, y: number }) => AppNode;
}

// Cache for node type definitions to avoid repeated API calls
let nodeTypeDefinitionsCache: Record<string, NodeTypeDefinition> | null = null;

// Utility function to generate unique short ID suffix
const generateUniqueIdSuffix = (): string => {
  // Generate a short random ID (6 characters)
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < 6; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

/**
 * Extract the base agent key from a unique node ID
 * @param uniqueId The unique node ID with suffix (e.g., "warren_buffett_abc123")
 * @returns The base agent key (e.g., "warren_buffett")
 */
export const extractBaseAgentKey = (uniqueId: string): string => {
  // For agent nodes, remove the last underscore and 6-character suffix
  // For other nodes like portfolio_manager, also remove the suffix
  const parts = uniqueId.split('_');
  if (parts.length >= 2) {
    const lastPart = parts[parts.length - 1];
    // If the last part is a 6-character alphanumeric string, it's likely our suffix
    if (lastPart.length === 6 && /^[a-z0-9]+$/.test(lastPart)) {
      return parts.slice(0, -1).join('_');
    }
  }
  return uniqueId; // Return original if no suffix pattern found
};

// Define base node creation functions (non-agent nodes) - 使用中英文对照
const baseNodeTypeDefinitions: Record<string, NodeTypeDefinition> = {
  // 中文名称映射
  "投资组合输入": {
    createNode: (position: { x: number, y: number }): AppNode => ({
      id: `portfolio-start-node_${generateUniqueIdSuffix()}`,
      type: "portfolio-start-node",
      position,
      data: {
        name: "投资组合输入",
        description: "输入您的投资组合，包括股票代码、股数和价格。将此节点连接到分析师以生成洞察。",
        status: "Idle",
      },
    }),
  },
  "投资组合管理": {
    createNode: (position: { x: number, y: number }): AppNode => ({
      id: `portfolio_manager_${generateUniqueIdSuffix()}`,
      type: "portfolio-manager-node",
      position,
      data: {
        name: "投资组合管理",
        description: "根据分析师的输入生成投资决策。",
        status: "Idle",
      },
    }),
  },
  "股票输入": {
    createNode: (position: { x: number, y: number }): AppNode => ({
      id: `stock-analyzer-node_${generateUniqueIdSuffix()}`,
      type: "stock-analyzer-node",
      position,
      data: {
        name: "股票输入",
        description: "输入个股代码并将此节点连接到分析师以生成洞察。",
        status: "Idle",
      },
    }),
  },
  // 保留英文名称映射以兼容旧数据
  "Portfolio Input": {
    createNode: (position: { x: number, y: number }): AppNode => ({
      id: `portfolio-start-node_${generateUniqueIdSuffix()}`,
      type: "portfolio-start-node",
      position,
      data: {
        name: "投资组合输入",
        description: "输入您的投资组合，包括股票代码、股数和价格。将此节点连接到分析师以生成洞察。",
        status: "Idle",
      },
    }),
  },
  "Portfolio Manager": {
    createNode: (position: { x: number, y: number }): AppNode => ({
      id: `portfolio_manager_${generateUniqueIdSuffix()}`,
      type: "portfolio-manager-node",
      position,
      data: {
        name: "投资组合管理",
        description: "根据分析师的输入生成投资决策。",
        status: "Idle",
      },
    }),
  },
  "Stock Input": {
    createNode: (position: { x: number, y: number }): AppNode => ({
      id: `stock-analyzer-node_${generateUniqueIdSuffix()}`,
      type: "stock-analyzer-node",
      position,
      data: {
        name: "股票输入",
        description: "输入个股代码并将此节点连接到分析师以生成洞察。",
        status: "Idle",
      },
    }),
  },
};

/**
 * Get all node type definitions, including agents fetched from the backend
 */
const getNodeTypeDefinitions = async (): Promise<Record<string, NodeTypeDefinition>> => {
  if (nodeTypeDefinitionsCache) {
    return nodeTypeDefinitionsCache;
  }

  const agents = await getAgents();
  
  // Create agent node definitions
  const agentNodeDefinitions = agents.reduce((acc: Record<string, NodeTypeDefinition>, agent: Agent) => {
    acc[agent.display_name] = {
      createNode: (position: { x: number, y: number }): AppNode => ({
        id: `${agent.key}_${generateUniqueIdSuffix()}`,
        type: "agent-node",
        position,
        data: {
          name: agent.display_name,
          description: agent.investing_style || "",
          status: "Idle",
        },
      }),
    };
    return acc;
  }, {});

  // Combine base and agent definitions
  nodeTypeDefinitionsCache = {
    ...baseNodeTypeDefinitions,
    ...agentNodeDefinitions,
  };

  return nodeTypeDefinitionsCache;
};

export async function getNodeTypeDefinition(componentName: string): Promise<NodeTypeDefinition | null> {
  const nodeTypeDefinitions = await getNodeTypeDefinitions();
  return nodeTypeDefinitions[componentName] || null;
}

// Get the node ID that would be generated for a component
export async function getNodeIdForComponent(componentName: string): Promise<string | null> {
  const nodeTypeDefinition = await getNodeTypeDefinition(componentName);
  if (!nodeTypeDefinition) {
    return null;
  }
  
  // Extract ID by creating a temporary node (position doesn't matter for ID extraction)
  const tempNode = nodeTypeDefinition.createNode({ x: 0, y: 0 });
  return tempNode.id;
}

/**
 * Clear the node type definitions cache - useful for testing or when you want to force a refresh
 */
export const clearNodeTypeDefinitionsCache = () => {
  nodeTypeDefinitionsCache = null;
};
