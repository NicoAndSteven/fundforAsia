import { useReactFlow, type NodeProps } from '@xyflow/react';
import { ChartLine, ChevronDown, Play, Square } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { CardContent } from '@/components/ui/card';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useFlowContext } from '@/contexts/flow-context';
import { useLayoutContext } from '@/contexts/layout-context';
import { useNodeContext } from '@/contexts/node-context';
import { useFlowConnection } from '@/hooks/use-flow-connection';
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts';
import { useNodeState } from '@/hooks/use-node-state';
import { cn, formatKeyboardShortcut } from '@/lib/utils';
import { type StockAnalyzerNode } from '../types';
import { NodeShell } from './node-shell';

const runModes = [
  { value: 'single', label: '单次运行' },
  { value: 'backtest', label: '回测' },
];

export function StockAnalyzerNode({
  data,
  selected,
  id,
  isConnectable,
}: NodeProps<StockAnalyzerNode>) {
  const today = new Date();
  const threeMonthsAgo = new Date(today);
  threeMonthsAgo.setMonth(today.getMonth() - 3);
  
  const [tickers, setTickers] = useNodeState(id, 'tickers', '000001,600000');
  const [runMode, setRunMode] = useNodeState(id, 'runMode', 'single');
  const [initialCash, setInitialCash] = useNodeState(id, 'initialCash', '100000');
  const [startDate, setStartDate] = useNodeState(id, 'startDate', threeMonthsAgo.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useNodeState(id, 'endDate', today.toISOString().split('T')[0]);
  const [open, setOpen] = useState(false);
  
  const { currentFlowId } = useFlowContext();
  const nodeContext = useNodeContext();
  const { getAllAgentModels } = nodeContext;
  const { getNodes, getEdges } = useReactFlow();
  const { expandBottomPanel, setBottomPanelTab } = useLayoutContext();
  
  const flowId = currentFlowId?.toString() || null;
  const {
    isConnecting,
    isConnected,
    isProcessing,
    canRun,
    runFlow,
    runBacktest,
    stopFlow,
    recoverFlowState
  } = useFlowConnection(flowId);
  
  const canRunHedgeFund = canRun && tickers.trim() !== '';
  
  useKeyboardShortcuts({
    shortcuts: [
      {
        key: 'Enter',
        ctrlKey: true,
        metaKey: true,
        callback: () => {
          if (canRunHedgeFund) {
            handlePlay();
          }
        },
        preventDefault: true,
      },
    ],
  });
  
  useEffect(() => {
    if (flowId) {
      recoverFlowState();
    }
  }, [flowId, recoverFlowState]);
  
  const handleTickersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTickers(e.target.value);
  };

  const handleInitialCashChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const numericValue = e.target.value.replace(/[^0-9.]/g, '');
    setInitialCash(numericValue);
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStartDate(e.target.value);
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEndDate(e.target.value);
  };

  const formatCurrency = (value: string) => {
    if (!value) return '';
    const num = parseFloat(value);
    if (isNaN(num)) return value;
    return num.toLocaleString('zh-CN');
  };

  const handleStop = () => {
    stopFlow();
  };

  const handlePlay = () => {
    if (runMode === 'backtest') {
      expandBottomPanel();
      setBottomPanelTab('output');
    }
    
    const allNodes = getNodes();
    const allEdges = getEdges();
    
    const reachableNodes = new Set<string>();
    const visited = new Set<string>();
    
    const dfs = (nodeId: string) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      
      if (nodeId !== id) {
        reachableNodes.add(nodeId);
      }
      
      const outgoingEdges = allEdges.filter(edge => edge.source === nodeId);
      for (const edge of outgoingEdges) {
        dfs(edge.target);
      }
    };
    
    dfs(id);
    
    const agentNodes = allNodes.filter(node => reachableNodes.has(node.id));
    
    const reachableNodeIds = new Set([id, ...reachableNodes]);
    const validEdges = allEdges.filter(edge => 
      reachableNodeIds.has(edge.source) && reachableNodeIds.has(edge.target)
    );

    const agentModels = [];
    const allAgentModels = getAllAgentModels(flowId);
    for (const node of agentNodes) {
      const model = allAgentModels[node.id];
      if (model) {
        agentModels.push({
          agent_id: node.id,
          model_name: model.model_name,
          model_provider: model.provider as any
        });
      }
    }
    
    const tickerList = tickers.split(',').map(t => t.trim());
    
    if (runMode === 'backtest') {
      runBacktest({
        tickers: tickerList,
        graph_nodes: agentNodes.map(node => ({
          id: node.id,
          type: node.type,
          data: node.data,
          position: node.position
        })),
        graph_edges: validEdges,
        agent_models: agentModels,
        start_date: startDate,
        end_date: endDate,
        initial_capital: parseFloat(initialCash) || 100000,
        margin_requirement: 0.0,
        model_name: undefined,
        model_provider: undefined,
      });
    } else {
      runFlow({
        tickers: tickerList,
        graph_nodes: agentNodes.map(node => ({
          id: node.id,
          type: node.type,
          data: node.data,
          position: node.position
        })),
        graph_edges: validEdges,
        agent_models: agentModels,
        model_name: undefined,
        model_provider: undefined,
        start_date: startDate,
        end_date: endDate,
      });
    }
  };

  const showAsProcessing = isConnecting || isConnected || isProcessing;

  return (
    <TooltipProvider>
      <NodeShell
        id={id}
        selected={selected}
        isConnectable={isConnectable}
        icon={<ChartLine className="h-5 w-5" />}
        name={data.name || "股票分析器"}
        description={data.description}
        hasLeftHandle={false}
      >
        <CardContent className="p-0">
          <div className="border-t border-border p-3">
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <div className="text-subtitle text-primary flex items-center gap-1">
                  <Tooltip delayDuration={200}>
                    <TooltipTrigger asChild>
                      <span>股票代码</span>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      多个股票代码用逗号分隔 (如: 000001,600000,300001)
                    </TooltipContent>
                  </Tooltip>
                </div>
                <Input
                  placeholder="输入股票代码"
                  value={tickers}
                  onChange={handleTickersChange}
                />
              </div>
              <div className="flex flex-col gap-2">
                <div className="text-subtitle text-primary flex items-center gap-1">
                  运行模式
                </div>
                <div className="flex gap-2">
                  <Popover open={open} onOpenChange={setOpen}>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="flex-1 justify-between h-10 px-3 py-2 bg-node border border-border hover:bg-accent"
                      >
                        <span className="text-subtitle">
                          {runModes.find((mode) => mode.value === runMode)?.label || '单次运行'}
                        </span>
                        <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0 bg-node border border-border shadow-lg">
                      <Command className="bg-node">
                        <CommandList className="bg-node">
                          <CommandEmpty>未找到运行模式</CommandEmpty>
                          <CommandGroup>
                            {runModes.map((mode) => (
                              <CommandItem
                                key={mode.value}
                                value={mode.value}
                                className={cn(
                                  "cursor-pointer bg-node hover:bg-accent",
                                  runMode === mode.value
                                )}
                                onSelect={(currentValue) => {
                                  setRunMode(currentValue);
                                  setOpen(false);
                                }}
                              >
                                {mode.label}
                              </CommandItem>
                            ))}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>
                  <Button 
                    size="icon" 
                    variant="secondary"
                    className="flex-shrink-0 transition-all duration-200 hover:bg-primary hover:text-primary-foreground active:scale-95"
                    title={showAsProcessing ? "停止" : `运行 (${formatKeyboardShortcut('↵')})`}
                    onClick={showAsProcessing ? handleStop : handlePlay}
                    disabled={!canRunHedgeFund && !showAsProcessing}
                  >
                    {showAsProcessing ? (
                      <Square className="h-3.5 w-3.5" />
                    ) : (
                      <Play className="h-3.5 w-3.5" />
                    )}
                  </Button>
                </div>
              </div>
              {runMode === 'backtest' && (
                <Accordion type="single" collapsible>
                  <AccordionItem value="advanced" className="border-none">
                    <AccordionTrigger className="!text-subtitle text-primary">
                      高级选项
                    </AccordionTrigger>
                    <AccordionContent className="pt-2">
                      <div className="flex flex-col gap-4">
                        <div className="flex flex-col gap-2">
                          <div className="text-subtitle text-primary flex items-center gap-1">
                            初始资金
                          </div>
                          <div className="relative flex-1">
                            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground pointer-events-none">
                              ¥
                            </div>
                            <Input
                              type="text"
                              placeholder="100,000"
                              value={formatCurrency(initialCash)}
                              onChange={handleInitialCashChange}
                              className="pl-8 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                            />
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          <div className="text-subtitle text-primary flex items-center gap-1">
                            开始日期
                          </div>
                          <Input
                            type="date"
                            value={startDate}
                            onChange={handleStartDateChange}
                          />
                        </div>
                        <div className="flex flex-col gap-2">
                          <div className="text-subtitle text-primary flex items-center gap-1">
                            结束日期
                          </div>
                          <Input
                            type="date"
                            value={endDate}
                            onChange={handleEndDateChange}
                          />
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              )}
              {runMode === 'single' && (
                <Accordion type="single" collapsible>
                  <AccordionItem value="advanced" className="border-none">
                    <AccordionTrigger className="!text-subtitle text-primary">
                      高级选项
                    </AccordionTrigger>
                    <AccordionContent className="pt-2">
                      <div className="flex flex-col gap-4">
                        <div className="flex flex-col gap-2">
                          <div className="text-subtitle text-primary flex items-center gap-1">
                            结束日期
                          </div>
                          <Input
                            type="date"
                            value={endDate}
                            onChange={handleEndDateChange}
                          />
                        </div>
                        <div className="flex flex-col gap-2">
                          <div className="text-subtitle text-primary flex items-center gap-1">
                            开始日期
                          </div>
                          <Input
                            type="date"
                            value={startDate}
                            onChange={handleStartDateChange}
                          />
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              )}
            </div>
          </div>
        </CardContent>
      </NodeShell>
    </TooltipProvider>
  );
}
