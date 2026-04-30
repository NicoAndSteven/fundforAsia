import { useReactFlow, type NodeProps } from '@xyflow/react';
import { ChevronDown, PieChart, Play, Plus, Search, Square, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { CardContent } from '@/components/ui/card';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
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
import { TickerAutocomplete } from '@/components/ticker-autocomplete';
import { fetchSectors, fetchSectorEtf, type SectorItem } from '@/services/market-service';
import { type PortfolioStartNode } from '../types';
import { NodeShell } from './node-shell';

interface PortfolioPosition {
  ticker: string;
  quantity: string;
  tradePrice: string;
}

const runModes = [
  { value: 'single', label: '单次运行' },
  { value: 'backtest', label: '回测' },
  { value: 'sector', label: '板块分析' },
];

export function PortfolioStartNode({
  data,
  selected,
  id,
  isConnectable,
}: NodeProps<PortfolioStartNode>) {
  // Calculate default dates
  const today = new Date();
  const threeMonthsAgo = new Date(today);
  threeMonthsAgo.setMonth(today.getMonth() - 3);
  
  // Use persistent state hooks
  const [positions, setPositions] = useNodeState<PortfolioPosition[]>(id, 'positions', [
    { ticker: '', quantity: '', tradePrice: '' },
  ]);
  const [initialCash, setInitialCash] = useNodeState(id, 'initialCash', '100000');
  const [runMode, setRunMode] = useNodeState(id, 'runMode', 'single');
  const [startDate, setStartDate] = useNodeState(id, 'startDate', threeMonthsAgo.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useNodeState(id, 'endDate', today.toISOString().split('T')[0]);
  const [useLlmJudgment, setUseLlmJudgment] = useNodeState(id, 'useLlmJudgment', true);
  const [open, setOpen] = useState(false);

  // Sector analysis state
  const [sectors, setSectors] = useState<SectorItem[]>([]);
  const [selectedSector, setSelectedSector] = useNodeState<SectorItem | null>(id, 'selectedSector', null);
  const [sectorEtfCode, setSectorEtfCode] = useState<string>('');
  const [loadingSectors, setLoadingSectors] = useState(false);
  const [loadingEtf, setLoadingEtf] = useState(false);
  const [sectorPopoverOpen, setSectorPopoverOpen] = useState(false);
  const sectorsFetched = useRef(false);

  // Fetch sector list when switching to sector mode
  useEffect(() => {
    if (runMode === 'sector' && !sectorsFetched.current) {
      sectorsFetched.current = true;
      setLoadingSectors(true);
      fetchSectors()
        .then(setSectors)
        .catch(() => setSectors([]))
        .finally(() => setLoadingSectors(false));
    }
    if (runMode !== 'sector') {
      sectorsFetched.current = false;
    }
  }, [runMode]);

  // When a sector is selected, look up its ETF and auto-fill the ticker
  useEffect(() => {
    if (selectedSector) {
      // First try the etf_code from the sector list
      if (selectedSector.etf_code) {
        setSectorEtfCode(selectedSector.etf_code);
        setPositions([{ ticker: selectedSector.etf_code, quantity: '', tradePrice: '' }]);
      } else {
        // Fall back to API lookup by name
        setLoadingEtf(true);
        fetchSectorEtf(selectedSector.code, selectedSector.name)
          .then(result => {
            const code = result.etf_code;
            setSectorEtfCode(code);
            setPositions([{ ticker: code, quantity: '', tradePrice: '' }]);
          })
          .catch(() => {
            setSectorEtfCode('');
          })
          .finally(() => setLoadingEtf(false));
      }
    }
  }, [selectedSector, setPositions]);
  
  const { currentFlowId } = useFlowContext();
  const nodeContext = useNodeContext();
  const { getAllAgentModels, globalDefaultModel } = nodeContext;
  const { getNodes, getEdges } = useReactFlow();
  const { expandBottomPanel, setBottomPanelTab } = useLayoutContext();
  
  // Use the new flow connection hook
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
  
  // Check if the portfolio analyzer can be run
  const canRunPortfolioAnalyzer = canRun && (
    runMode === 'sector'
      ? selectedSector !== null && sectorEtfCode !== ''
      : positions.length > 0 && positions.every(pos => pos.ticker.trim() !== '')
  );
  
  // Add keyboard shortcut for Cmd+Enter / Ctrl+Enter to run portfolio analyzer
  useKeyboardShortcuts({
    shortcuts: [
      {
        key: 'Enter',
        ctrlKey: true,
        metaKey: true,
        callback: () => {
          if (canRunPortfolioAnalyzer) {
            handlePlay();
          }
        },
        preventDefault: true,
      },
    ],
  });
  
  // Recover flow state when component mounts or flow changes
  useEffect(() => {
    if (flowId) {
      recoverFlowState();
    }
  }, [flowId, recoverFlowState]);
  
  const handlePositionChange = (index: number, field: keyof PortfolioPosition, value: string) => {
    const newPositions = [...positions];
    newPositions[index][field] = value;
    setPositions(newPositions);
  };

  const addPosition = () => {
    setPositions([...positions, { ticker: '', quantity: '', tradePrice: '' }]);
  };

  const removePosition = (index: number) => {
    const newPositions = positions.filter((_, i) => i !== index);
    setPositions(newPositions);
  };

  const handleInitialCashChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInitialCash(e.target.value);
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStartDate(e.target.value);
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEndDate(e.target.value);
  };

  const handleStop = () => {
    stopFlow();
  };

  const handlePlay = () => {
    // Expand bottom panel and set to output tab if backtest or sector
    if (runMode === 'backtest' || runMode === 'sector') {
      expandBottomPanel();
      setBottomPanelTab('output');
    }
    
    // Get the current flow's nodes and edges
    const allNodes = getNodes();
    const allEdges = getEdges();
    
    // Find all nodes that are reachable from the portfolio-analyzer-node
    const reachableNodes = new Set<string>();
    const visited = new Set<string>();
    
    // DFS to find all reachable nodes
    const dfs = (nodeId: string) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      
      // If this is not the portfolio-analyzer-node itself, add it to reachable nodes
      if (nodeId !== id) {
        reachableNodes.add(nodeId);
      }
      
      // Find all outgoing edges from this node
      const outgoingEdges = allEdges.filter(edge => edge.source === nodeId);
      for (const edge of outgoingEdges) {
        dfs(edge.target);
      }
    };
    
    // Start DFS from the portfolio-analyzer-node
    dfs(id);
    
    // Filter nodes to only include reachable ones
    const agentNodes = allNodes.filter(node => reachableNodes.has(node.id));
    
    // Filter edges to only include connections between reachable nodes (plus the portfolio-analyzer-node)
    const reachableNodeIds = new Set([id, ...reachableNodes]);
    const validEdges = allEdges.filter(edge => 
      reachableNodeIds.has(edge.source) && reachableNodeIds.has(edge.target)
    );

    // Collect agent models from all agent nodes
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
    
    // Convert positions to the expected format for backend use
    const portfolioPositions = positions
      .filter(pos => pos.ticker.trim() !== '' && pos.quantity.trim() !== '' && pos.tradePrice.trim() !== '')
      .map(pos => ({
        ticker: pos.ticker.trim(),
        quantity: parseFloat(pos.quantity) || 0,
        trade_price: parseFloat(pos.tradePrice) || 0
      }));
    
    // For now, extract tickers for current API compatibility
    const tickerList = positions.map(pos => pos.ticker.trim()).filter(ticker => ticker !== '');
    
    // Check if we're in backtest or sector mode
    if (runMode === 'backtest' || runMode === 'sector') {
      // Use the flow connection hook to run the backtest with selected dates
      runBacktest({
        tickers: tickerList,
        // Send the actual graph structure instead of just selected analysts
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
        margin_requirement: 0.0, // Default margin requirement
        model_name: globalDefaultModel?.model_name || undefined,
        model_provider: globalDefaultModel?.provider || undefined,
        // Pass portfolio positions to backend
        portfolio_positions: portfolioPositions,
        use_llm_judgment: useLlmJudgment,
      });
    } else {
      // Use the regular hedge fund API for single run
      runFlow({
        tickers: tickerList,
        // Send the actual graph structure instead of just selected agents
        graph_nodes: agentNodes.map(node => ({
          id: node.id,
          type: node.type,
          data: node.data,
          position: node.position
        })),
        graph_edges: validEdges,
        agent_models: agentModels,
        model_name: globalDefaultModel?.model_name || undefined,
        model_provider: globalDefaultModel?.provider || undefined,
        start_date: threeMonthsAgo.toISOString().split('T')[0],
        end_date: today.toISOString().split('T')[0],
        initial_cash: parseFloat(initialCash) || 100000,
        // Pass portfolio positions to backend
        portfolio_positions: portfolioPositions,
        use_llm_judgment: useLlmJudgment,
      });
    }
  };

  // Determine if we're processing (connecting, connected, or any agents running)
  const showAsProcessing = isConnecting || isConnected || isProcessing;

  return (
    <TooltipProvider>
      <NodeShell
        id={id}
        selected={selected}
        isConnectable={isConnectable}
        icon={<PieChart className="h-5 w-5" />}
        name={data.name || "Portfolio Analyzer"}
        description={data.description}
        hasLeftHandle={false}
        width="w-80"
      >
        <CardContent className="p-0">
          <div className="border-t border-border p-3">
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <div className="text-subtitle text-primary flex items-center gap-1">
                  Available Cash
                </div>
                <div className="relative flex-1">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground pointer-events-none">
                    $
                  </div>
                  <Input
                    type="number"
                    placeholder="金额"
                    value={initialCash}
                    onChange={handleInitialCashChange}
                    className="pl-8 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
              {runMode === 'sector' ? (
                /* ── 板块选择（板块分析模式） ── */
                <div className="flex flex-col gap-2">
                  <div className="text-subtitle text-primary flex items-center gap-1">选择板块</div>
                  <Popover open={sectorPopoverOpen} onOpenChange={setSectorPopoverOpen}>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={sectorPopoverOpen}
                        className="w-full justify-between h-10 px-3 py-2 bg-node border border-border hover:bg-accent"
                      >
                        <span className="text-subtitle truncate">
                          {loadingSectors ? '加载板块中...' : selectedSector ? selectedSector.name : '搜索板块...'}
                        </span>
                        <Search className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0 bg-node border border-border shadow-lg">
                      <Command className="bg-node">
                        <CommandInput placeholder="搜索板块..." />
                        <CommandList className="bg-node">
                          <CommandEmpty>未找到板块</CommandEmpty>
                          <CommandGroup>
                            {sectors.slice(0, 50).map(sector => (
                              <CommandItem
                                key={sector.code}
                                value={`${sector.name} ${sector.code}`}
                                className={cn(
                                  "cursor-pointer bg-node hover:bg-accent",
                                  selectedSector?.code === sector.code && "bg-accent"
                                )}
                                onSelect={() => {
                                  setSelectedSector(sector);
                                  setSectorPopoverOpen(false);
                                }}
                              >
                                <div className="flex items-center justify-between w-full">
                                  <span>{sector.name}</span>
                                  <span className="text-xs text-muted-foreground">{sector.code}</span>
                                </div>
                              </CommandItem>
                            ))}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>

                  {/* 显示对应ETF */}
                  {loadingEtf && (
                    <div className="text-xs text-muted-foreground animate-pulse">查询对应ETF中...</div>
                  )}
                  {selectedSector && !loadingEtf && sectorEtfCode && (
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-muted-foreground">对应ETF:</span>
                      <span className="font-mono font-semibold text-primary">{sectorEtfCode}</span>
                    </div>
                  )}
                  {selectedSector && !loadingEtf && !sectorEtfCode && (
                    <div className="text-xs text-amber-500">该板块暂无对应ETF</div>
                  )}
                </div>
              ) : (
                /* ── 手动输入股票（Single / Backtest 模式） ── */
                <div className="flex flex-col gap-2">
                  <div className="text-subtitle text-primary flex items-center gap-1">
                    <Tooltip delayDuration={200}>
                      <TooltipTrigger asChild>
                        <span>Positions</span>
                      </TooltipTrigger>
                      <TooltipContent side="right">
                        Add your portfolio positions with ticker, quantity, and trade price
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex flex-col gap-2">
                    {positions.map((position, index) => {
                      return (
                      <div key={index} className="flex gap-2 items-center">
                        <TickerAutocomplete
                          value={position.ticker}
                          onChange={(value) => handlePositionChange(index, 'ticker', value)}
                          placeholder="代码或名称搜索"
                          className="flex-1"
                        />
                        <Input
                          type="number"
                          placeholder="数量"
                          value={position.quantity}
                          onChange={(e) => handlePositionChange(index, 'quantity', e.target.value)}
                          className="w-20"
                          step="any"
                        />
                        <div className="relative flex-1">
                          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground pointer-events-none">
                            $
                          </div>
                          <Input
                            type="number"
                            placeholder="价格"
                            value={position.tradePrice}
                            onChange={(e) => handlePositionChange(index, 'tradePrice', e.target.value)}
                            className="pl-8"
                            step="0.01"
                            min="0"
                          />
                        </div>
                        {positions.length > 1 && (
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => removePosition(index)}
                            className="flex-shrink-0 h-8 w-4 text-muted-foreground hover:text-destructive"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      );
                    })}
                    <Button
                      onClick={addPosition}
                      className="w-full mt-2 transition-all duration-200 hover:bg-primary hover:text-primary-foreground active:scale-95"
                      size="sm"
                      variant="secondary"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Position
                    </Button>
                  </div>
                </div>
              )}
              <div className="flex flex-col gap-2">
                <div className="text-subtitle text-primary flex items-center gap-1">
                  Run
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
                          {runModes.find((mode) => mode.value === runMode)?.label || 'Single Analysis'}
                        </span>
                        <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0 bg-node border border-border shadow-lg">
                      <Command className="bg-node">
                        <CommandList className="bg-node">
                          <CommandEmpty>No run mode found.</CommandEmpty>
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
                    disabled={!canRunPortfolioAnalyzer && !showAsProcessing}
                  >
                    {showAsProcessing ? (
                      <Square className="h-3.5 w-3.5" />
                    ) : (
                      <Play className="h-3.5 w-3.5" />
                    )}
                  </Button>
                </div>
              </div>
              {(runMode === 'backtest' || runMode === 'sector') && (
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col gap-2">
                    <div className="text-subtitle text-primary flex items-center gap-1">
                      Start Date
                    </div>
                    <Input
                      type="date"
                      value={startDate}
                      onChange={handleStartDateChange}
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <div className="text-subtitle text-primary flex items-center gap-1">
                      End Date
                    </div>
                    <Input
                      type="date"
                      value={endDate}
                      onChange={handleEndDateChange}
                    />
                  </div>

                  {/* ── AI 最终研判开关 ── */}
                  <label className="flex items-center justify-between gap-3 cursor-pointer group">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-subtitle text-primary group-hover:text-accent-foreground transition-colors">
                        AI 最终研判
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {useLlmJudgment ? 'LLM 信号生成（调用 API）' : '规则打分（无需 API）'}
                      </span>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-checked={useLlmJudgment}
                      onClick={() => setUseLlmJudgment(!useLlmJudgment)}
                      className={cn(
                        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
                        useLlmJudgment ? "bg-primary" : "bg-muted"
                      )}
                    >
                      <span
                        className={cn(
                          "pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform",
                          useLlmJudgment ? "translate-x-4" : "translate-x-0"
                        )}
                      />
                    </button>
                  </label>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </NodeShell>
    </TooltipProvider>
  );
}
