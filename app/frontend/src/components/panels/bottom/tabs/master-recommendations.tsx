import { useFlowContext } from '@/contexts/flow-context';
import { useNodeContext } from '@/contexts/node-context';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import {
  TrendingUp, TrendingDown, Award, Star, Users,
  Brain, Crown, Sparkles,
} from 'lucide-react';
import {
  calculateAnalystWinRate,
  getAnalystDisplayName, type AnalystWinRate,
} from './consensus-tab-utils';

/* ------------------------------------------------------------------ */
/*  Types (client-side aggregation fallback)                            */
/* ------------------------------------------------------------------ */

interface MasterStockPick {
  ticker: string;
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
}

interface MasterPicks {
  analystKey: string;
  displayName: string;
  bullish: MasterStockPick[];
  bearish: MasterStockPick[];
  neutral: MasterStockPick[];
}

interface ConsensusItem {
  ticker: string;
  score: number;
  bullish: number;
  bearish: number;
  neutral: number;
  total: number;
  topMasters: { name: string; confidence: number }[];
}

/* ------------------------------------------------------------------ */
/*  Helpers (client-side fallback)                                     */
/* ------------------------------------------------------------------ */

function normalise(signalData: unknown): { signal: string; confidence: number } | null {
  if (!signalData || typeof signalData !== 'object') return null;
  const d = signalData as Record<string, unknown>;
  const signal = typeof d.signal === 'string' ? d.signal.toUpperCase() : 'NEUTRAL';
  const confidence =
    typeof d.confidence === 'number' ? d.confidence
      : typeof d.confidence === 'string' ? parseFloat(d.confidence) || 0 : 0;
  return { signal, confidence };
}

function buildMasterPicks(signals: Record<string, unknown>): MasterPicks[] {
  const result: MasterPicks[] = [];
  for (const [agent, tickers] of Object.entries(signals)) {
    if (!tickers || typeof tickers !== 'object') continue;
    const bullish: MasterStockPick[] = [];
    const bearish: MasterStockPick[] = [];
    const neutral: MasterStockPick[] = [];
    for (const [ticker, signalData] of Object.entries(tickers as Record<string, unknown>)) {
      const n = normalise(signalData);
      if (!n) continue;
      const pick: MasterStockPick = { ticker, signal: n.signal as MasterStockPick['signal'], confidence: n.confidence };
      if (n.signal === 'BULLISH') bullish.push(pick);
      else if (n.signal === 'BEARISH') bearish.push(pick);
      else neutral.push(pick);
    }
    if (bullish.length === 0 && bearish.length === 0 && neutral.length === 0) continue;
    result.push({
      analystKey: agent,
      displayName: getAnalystDisplayName(agent),
      bullish: bullish.sort((a, b) => b.confidence - a.confidence),
      bearish: bearish.sort((a, b) => b.confidence - a.confidence),
      neutral,
    });
  }
  return result.sort((a, b) => (b.bullish.length - b.bearish.length) - (a.bullish.length - a.bearish.length));
}

function buildConsensus(signals: Record<string, unknown>): ConsensusItem[] {
  const map = new Map<string, { bullish: number; bearish: number; neutral: number; top: { name: string; confidence: number }[] }>();
  for (const [agent, tickers] of Object.entries(signals)) {
    if (!tickers || typeof tickers !== 'object') continue;
    for (const [ticker, signalData] of Object.entries(tickers as Record<string, unknown>)) {
      const n = normalise(signalData);
      if (!n) continue;
      if (!map.has(ticker)) map.set(ticker, { bullish: 0, bearish: 0, neutral: 0, top: [] });
      const entry = map.get(ticker)!;
      if (n.signal === 'BULLISH') { entry.bullish++; entry.top.push({ name: agent, confidence: n.confidence }); }
      else if (n.signal === 'BEARISH') entry.bearish++;
      else entry.neutral++;
    }
  }
  const items: ConsensusItem[] = [];
  for (const [ticker, data] of map) {
    const total = data.bullish + data.bearish + data.neutral;
    const score = total > 0 ? (data.bullish - data.bearish) / total : 0;
    data.top.sort((a, b) => b.confidence - a.confidence);
    items.push({ ticker, score, ...data, total, topMasters: data.top.slice(0, 3) });
  }
  return items.sort((a, b) => b.score - a.score);
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function SummaryBanner({ summary }: { summary: string }) {
  if (!summary) return null;
  return (
    <div className="flex items-start gap-2 px-4 py-3 rounded-lg border bg-gradient-to-r from-primary/5 to-primary/10 mb-4">
      <Sparkles size={16} className="text-primary mt-0.5 shrink-0" />
      <p className="text-sm text-muted-foreground leading-relaxed">{summary}</p>
    </div>
  );
}

function ConsensusPicks({ items }: { items: ConsensusItem[] }) {
  if (items.length === 0) return null;
  const top = items.slice(0, 8);

  return (
    <section className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Award size={18} className="text-yellow-500" />
        <h3 className="text-sm font-semibold">大师共识精选</h3>
        <span className="text-xs text-muted-foreground ml-auto">
          基于 {top.reduce((s, i) => s + i.total, 0)} 位分析师综合信号
        </span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {top.map((item, idx) => {
          const maxCount = Math.max(item.bullish, item.bearish, 1);
          return (
            <div key={item.ticker} className="rounded-lg border bg-card hover:bg-accent/5 transition-colors overflow-hidden">
              <div className={cn("px-3 py-2 flex items-center justify-between border-b", idx === 0 ? "bg-yellow-500/10" : "bg-muted/20")}>
                <div className="flex items-center gap-1.5">
                  {idx === 0 && <Crown size={14} className="text-yellow-500" />}
                  <span className="font-semibold text-sm">{item.ticker}</span>
                </div>
                <span className={cn("text-xs font-bold", item.score > 0.3 ? "text-green-500" : item.score < -0.3 ? "text-red-500" : "text-muted-foreground")}>
                  {item.score > 0 ? '+' : ''}{(item.score * 100).toFixed(0)}
                </span>
              </div>
              <div className="p-3 space-y-2">
                <div className="flex h-1.5 rounded-full overflow-hidden bg-muted">
                  <div className="bg-green-500 transition-all" style={{ width: `${(item.bullish / maxCount) * 50}%` }} />
                  <div className="bg-red-500 transition-all" style={{ width: `${(item.bearish / maxCount) * 50}%` }} />
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-green-600 dark:text-green-400 font-medium">
                    <TrendingUp size={12} className="inline mr-0.5" />{item.bullish}
                  </span>
                  <span className="text-muted-foreground">{item.neutral}</span>
                  <span className="text-red-600 dark:text-red-400 font-medium">
                    <TrendingDown size={12} className="inline mr-0.5" />{item.bearish}
                  </span>
                </div>
                {item.topMasters.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {item.topMasters.map(m => (
                      <span key={m.name} className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-green-500/10 text-green-600 dark:text-green-400">
                        {getAnalystDisplayName(m.name)}
                        <span className="opacity-70">{m.confidence.toFixed(0)}%</span>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function MasterCard({ master, winRate }: { master: MasterPicks; winRate?: AnalystWinRate }) {
  const hasBullish = master.bullish.length > 0;
  const hasBearish = master.bearish.length > 0;

  return (
    <div className="rounded-lg border bg-card hover:bg-accent/5 transition-colors overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/20">
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-primary" />
          <span className="font-semibold text-sm">{master.displayName}</span>
        </div>
        {winRate && winRate.totalPredictions > 0 && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted-foreground">胜率</span>
            <span className={cn("font-bold", winRate.winRate >= 60 ? "text-green-500" : winRate.winRate >= 40 ? "text-yellow-500" : "text-red-500")}>
              {winRate.winRate.toFixed(1)}%
            </span>
            <span className="text-muted-foreground">({winRate.correctPredictions}/{winRate.totalPredictions})</span>
          </div>
        )}
      </div>
      <div className="p-3 space-y-2">
        {hasBullish && (
          <div>
            <div className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400 mb-1.5 font-medium">
              <TrendingUp size={12} /> 看多
            </div>
            <div className="flex flex-wrap gap-1.5">
              {master.bullish.map(pick => (
                <span key={pick.ticker} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-green-500/10 text-green-700 dark:text-green-300 border border-green-500/20">
                  {pick.ticker}
                  <span className="opacity-60">{pick.confidence.toFixed(0)}%</span>
                </span>
              ))}
            </div>
          </div>
        )}
        {hasBearish && (
          <div>
            <div className="flex items-center gap-1 text-xs text-red-600 dark:text-red-400 mb-1.5 font-medium">
              <TrendingDown size={12} /> 看空
            </div>
            <div className="flex flex-wrap gap-1.5">
              {master.bearish.map(pick => (
                <span key={pick.ticker} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-red-500/10 text-red-700 dark:text-red-300 border border-red-500/20">
                  {pick.ticker}
                  <span className="opacity-60">{pick.confidence.toFixed(0)}%</span>
                </span>
              ))}
            </div>
          </div>
        )}
        {!hasBullish && !hasBearish && (
          <div className="text-xs text-muted-foreground py-2 text-center">无明确信号</div>
        )}
      </div>
    </div>
  );
}

function MasterDetail({ masters, winRates }: { masters: MasterPicks[]; winRates: AnalystWinRate[] }) {
  if (masters.length === 0) return null;
  const winRateMap = new Map(winRates.map(w => [w.analystKey, w]));

  return (
    <section>
      <div className="flex items-center gap-2 mb-3">
        <Users size={18} className="text-primary" />
        <h3 className="text-sm font-semibold">各大师推荐明细</h3>
        <span className="text-xs text-muted-foreground ml-auto">{masters.length} 位分析师</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        {masters.map(master => (
          <MasterCard key={master.analystKey} master={master} winRate={winRateMap.get(master.analystKey)} />
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Main component                                                     */
/* ------------------------------------------------------------------ */

interface MasterRecommendationsProps {
  className?: string;
}

export function MasterRecommendations({ className }: MasterRecommendationsProps) {
  const { currentFlowId } = useFlowContext();
  const { getAgentNodeDataForFlow, getOutputNodeDataForFlow } = useNodeContext();
  const [, setUpdateTrigger] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setUpdateTrigger(t => t + 1), 1500);
    return () => clearInterval(id);
  }, []);

  const flowId = currentFlowId?.toString() || null;
  const agentData = getAgentNodeDataForFlow(flowId);
  const outputData = getOutputNodeDataForFlow(flowId);

  const isBacktestRun = !!(agentData && agentData['backtest']);
  const backtestResults: unknown[] = isBacktestRun
    ? (agentData['backtest'] as unknown as Record<string, unknown>)?.backtestResults as unknown[] || []
    : [];

  // ── Use server-side master_report when available ──
  const masterReport = outputData?.master_report;

  if (masterReport) {
    // Render from pre-aggregated report
    const consensusItems: ConsensusItem[] = (masterReport.consensus_picks || []).map(p => ({
      ticker: p.ticker,
      score: p.consensus_score,
      bullish: p.bullish_count,
      bearish: p.bearish_count,
      neutral: p.neutral_count,
      total: p.total_analysts,
      topMasters: p.top_bullish_analysts.map(name => ({ name, confidence: 100 })),
    }));

    const masterPicks: MasterPicks[] = Object.entries(masterReport.master_picks || {}).map(([key, picks]) => ({
      analystKey: key,
      displayName: getAnalystDisplayName(key),
      bullish: picks.filter(p => p.signal === 'BULLISH').map(p => ({ ticker: p.ticker, signal: p.signal as 'BULLISH', confidence: p.confidence })),
      bearish: picks.filter(p => p.signal === 'BEARISH').map(p => ({ ticker: p.ticker, signal: p.signal as 'BEARISH', confidence: p.confidence })),
      neutral: picks.filter(p => p.signal === 'NEUTRAL').map(p => ({ ticker: p.ticker, signal: p.signal as 'NEUTRAL', confidence: p.confidence })),
    }));

    const winRates: AnalystWinRate[] = (masterReport.master_performances || []).map(p => ({
      analystKey: p.analyst_key,
      displayName: p.analyst_name,
      totalPredictions: p.total_predictions,
      correctPredictions: p.correct_predictions,
      winRate: p.win_rate,
      recentWinRate: p.win_rate,
      recentTrend: 0,
    }));

    const hasData = consensusItems.length > 0 || masterPicks.length > 0;

    return (
      <div className={cn("h-full overflow-y-auto", className)}>
        {!hasData && (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Star size={32} className="mb-3 opacity-30" />
            <p className="text-sm">暂无大师推荐数据</p>
            <p className="text-xs mt-1">运行板块分析后此处将展示各投资大师的股票推荐</p>
          </div>
        )}
        {hasData && (
          <div className="space-y-4">
            {masterReport.summary && <SummaryBanner summary={masterReport.summary} />}
            <ConsensusPicks items={consensusItems} />
            <MasterDetail masters={masterPicks} winRates={winRates} />
          </div>
        )}
      </div>
    );
  }

  // ── Fallback: client-side aggregation (for backward compatibility) ──
  let analystSignals: Record<string, unknown> | null = null;
  let analystWinRates: AnalystWinRate[] = [];

  if (isBacktestRun && backtestResults.length > 0) {
    const latest = backtestResults[backtestResults.length - 1] as unknown as Record<string, unknown>;
    if (latest?.analyst_signals) {
      analystSignals = latest.analyst_signals as unknown as Record<string, unknown>;
    }
    analystWinRates = calculateAnalystWinRate(backtestResults);
  } else if (outputData?.analyst_signals) {
    analystSignals = outputData.analyst_signals as unknown as Record<string, unknown>;
  }

  const clientPicks = analystSignals ? buildMasterPicks(analystSignals) : [];
  const clientConsensus = analystSignals ? buildConsensus(analystSignals) : [];
  const hasClientData = clientPicks.length > 0;

  return (
    <div className={cn("h-full overflow-y-auto", className)}>
      {!hasClientData && (
        <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
          <Star size={32} className="mb-3 opacity-30" />
          <p className="text-sm">暂无大师推荐数据</p>
          <p className="text-xs mt-1">运行分析或回测后此处将展示各投资大师的股票推荐</p>
        </div>
      )}
      {hasClientData && (
        <div className="space-y-6">
          <ConsensusPicks items={clientConsensus} />
          <MasterDetail masters={clientPicks} winRates={analystWinRates} />
        </div>
      )}
    </div>
  );
}
