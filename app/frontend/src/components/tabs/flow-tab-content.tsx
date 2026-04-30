import { Flow } from '@/components/Flow';
import { useFlowContext } from '@/contexts/flow-context';
import { setNodeInternalState, setCurrentFlowId as setNodeStateFlowId } from '@/hooks/use-node-state';
import { cn } from '@/lib/utils';
import { Flow as FlowType } from '@/types/flow';
import { useEffect, useRef } from 'react';

// Import the flow connection manager to check if flow is actively running

interface FlowTabContentProps {
  flow: FlowType;
  className?: string;
}

export function FlowTabContent({ flow, className }: FlowTabContentProps) {
  const { loadFlow } = useFlowContext();
  const initializedRef = useRef(false);

  // Enhanced load function that restores both use-node-state and node context data
  const loadFlowWithCompleteState = async (flowToLoad: FlowType) => {
    try {
      const flowId = flowToLoad.id.toString();

      // First, set the flow ID for node state isolation
      setNodeStateFlowId(flowId);

      // DO NOT clear configuration state when switching tabs - useNodeState handles flow isolation automatically
      // DO NOT reset runtime data when switching tabs - preserve all runtime state
      // Runtime data should only be reset when explicitly starting a new run via the Play button
      console.log(`[FlowTabContent] Loading flow ${flowId}, preserving all state (configuration + runtime)`);

      // Load the flow using the basic context function (handles React Flow state)
      await loadFlow(flowToLoad);

      // Then restore internal states for each node (use-node-state data)
      if (flowToLoad.nodes) {
        flowToLoad.nodes.forEach((node: any) => {
          if (node.data?.internal_state) {
            setNodeInternalState(node.id, node.data.internal_state);
          }
        });
      }

      // NOTE: We intentionally do NOT restore nodeContextData here
      // Runtime execution data (messages, analysis, agent status) should start fresh
      // Only configuration data (tickers, model selections) is restored above
    } catch (error) {
      console.error('Failed to load flow with complete state:', error);
      throw error;
    }
  };

  // Load the flow only ONCE on mount, do NOT reload from API on every tab switch back
  useEffect(() => {
    if (!initializedRef.current) {
      initializedRef.current = true;
      loadFlowWithCompleteState(flow);
    }
  }, [flow, loadFlow]);

  return (
    <div className={cn("h-full w-full", className)}>
      <Flow />
    </div>
  );
}
