import { useFlowContext } from '@/contexts/flow-context';
import { useNodeContext } from '@/contexts/node-context';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import {
  calculateStockConsensus,
  calculateAnalystWinRate,
  buildSignalMatrix,
  type StockConsensus,
  type AnalystWinRate,
} from './consensus-tab-utils';
import { AnalystLeaderboard } from './consensus/analyst-leaderboard';
import { StockRanker } from './consensus/stock-ranker';
import { SignalMatrix } from './consensus/signal-matrix';

interface ConsensusTabProps {
  className?: string;
}

export function ConsensusTab({ className }: ConsensusTabProps) {
  const { currentFlowId } = useFlowContext();
  const { getAgentNodeDataForFlow, getOutputNodeDataForFlow } = useNodeContext();
  const [updateTrigger, setUpdateTrigger] = useState(0);

  const agentData = getAgentNodeDataForFlow(currentFlowId?.toString() || null);
  const outputData = getOutputNodeDataForFlow(currentFlowId?.toString() || null);

  // Force re-render periodically to show real-time updates during backtest
  useEffect(() => {
    const interval = setInterval(() => {
      setUpdateTrigger(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Suppress unused warning — updateTrigger is used in the JSX
  void updateTrigger;

  const isBacktestRun = !!(agentData && agentData['backtest']);
  const backtestResults = isBacktestRun
    ? (agentData['backtest'] as any)?.backtestResults || []
    : [];

  // Calculate derived data
  let stockConsensus: StockConsensus[] = [];
  let analystWinRates: AnalystWinRate[] = [];

  if (isBacktestRun && backtestResults.length > 0) {
    // For backtest mode, use the latest day's analyst_signals for consensus
    const latestResult = backtestResults[backtestResults.length - 1];
    if (latestResult?.analyst_signals) {
      stockConsensus = calculateStockConsensus(latestResult.analyst_signals);
    }
    analystWinRates = calculateAnalystWinRate(backtestResults);
  } else if (outputData?.analyst_signals) {
    // For regular run mode
    stockConsensus = calculateStockConsensus(outputData.analyst_signals);
  }

  const { rows: matrixRows, analystKeys } = outputData?.analyst_signals
    ? buildSignalMatrix(outputData.analyst_signals)
    : { rows: [], analystKeys: [] };

  const hasData = stockConsensus.length > 0 || analystWinRates.length > 0 || matrixRows.length > 0;

  return (
    <div className={cn("h-full overflow-y-auto", className)}>
      {!hasData && (
        <div className="text-center py-12 text-muted-foreground">
          <p className="text-sm">暂无共识数据</p>
          <p className="text-xs mt-1">运行分析后此处将显示分析师共识和股票排行</p>
        </div>
      )}

      {hasData && (
        <div className="space-y-4">
          {/* In backtest mode, show leaderboard first (most important) */}
          {isBacktestRun && analystWinRates.length > 0 && (
            <AnalystLeaderboard analystWinRates={analystWinRates} />
          )}

          {/* Stock consensus ranking */}
          {stockConsensus.length > 0 && (
            <StockRanker stockConsensus={stockConsensus} />
          )}

          {/* Signal matrix */}
          {matrixRows.length > 0 && (
            <SignalMatrix rows={matrixRows} analystKeys={analystKeys} />
          )}
        </div>
      )}
    </div>
  );
}
