import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { API_BASE_URL } from '@/services/api';
import { Loader2, TrendingUp, TrendingDown, Brain, Award, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface MasterReport {
  summary: string;
  consensus_picks: Array<{
    ticker: string;
    consensus_score: number;
    bullish_count: number;
    bearish_count: number;
    neutral_count: number;
    total_analysts: number;
    top_bullish_analysts: string[];
  }>;
  master_performances: Array<{
    analyst_key: string;
    analyst_name: string;
    total_predictions: number;
    correct_predictions: number;
    win_rate: number;
  }>;
  master_picks: Record<string, Array<{ ticker: string; signal: string; confidence: number }>>;
}

interface QuickResult {
  success: boolean;
  tickers: string[];
  lookback_days: number;
  total_days: number;
  master_report: MasterReport;
  performance_metrics: Record<string, any>;
}

/* ------------------------------------------------------------------ */
/*  Component                                                         */
/* ------------------------------------------------------------------ */

function ConsensusScore({ score }: { score: number }) {
  const pct = Math.round((score + 1) * 50);
  const color = score > 0.3 ? 'text-green-500' : score < -0.3 ? 'text-red-500' : 'text-yellow-500';
  const bg = score > 0.3 ? 'bg-green-500' : score < -0.3 ? 'bg-red-500' : 'bg-yellow-500';

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
        <div className={cn('h-full rounded-full transition-all', bg)} style={{ width: `${pct}%` }} />
      </div>
      <span className={cn('text-xs font-bold w-8 text-right', color)}>
        {score > 0 ? '+' : ''}{score.toFixed(2)}
      </span>
    </div>
  );
}

export function QuickAnalysis() {
  const [ticker, setTicker] = useState('');
  const [days, setDays] = useState('60');
  const [useLlmJudgment, setUseLlmJudgment] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QuickResult | null>(null);
  const [error, setError] = useState('');
  const [open, setOpen] = useState(false);

  const handleAnalyze = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const resp = await fetch(`${API_BASE_URL}/hedge-fund/quick-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: [ticker.trim().toUpperCase()],
          lookback_days: parseInt(days),
          use_llm_judgment: useLlmJudgment,
        }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${resp.status}`);
      }

      const data: QuickResult = await resp.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message || '分析失败');
    } finally {
      setLoading(false);
    }
  };

  const report = result?.master_report;
  const consensusPicks = report?.consensus_picks || [];
  const performances = report?.master_performances || [];
  const summary = report?.summary || '';

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Sparkles size={14} />
          一键分析
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles size={18} className="text-primary" />
            大师一键分析
          </DialogTitle>
        </DialogHeader>

        {/* ── Input area ── */}
        <div className="flex items-end gap-3">
          <div className="flex-1 space-y-1">
            <Label htmlFor="ticker" className="text-xs">股票/ETF 代码</Label>
            <Input
              id="ticker"
              placeholder="如 512480"
              value={ticker}
              onChange={e => setTicker(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
            />
          </div>
          <div className="w-28 space-y-1">
            <Label className="text-xs">回看天数</Label>
            <Select value={days} onValueChange={setDays}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="30">30 天</SelectItem>
                <SelectItem value="60">60 天</SelectItem>
                <SelectItem value="90">90 天</SelectItem>
                <SelectItem value="180">180 天</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleAnalyze} disabled={loading || !ticker.trim()}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : '分析'}
          </Button>
        </div>

        {/* ── AI 最终研判开关 ── */}
        <div className="flex items-center justify-between px-1">
          <span className="text-xs text-muted-foreground">
            {useLlmJudgment ? 'LLM 信号生成' : '规则打分'}
          </span>
          <button
            type="button"
            role="switch"
            aria-checked={useLlmJudgment}
            onClick={() => setUseLlmJudgment(!useLlmJudgment)}
            className={cn(
              "relative inline-flex h-4 w-7 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors",
              useLlmJudgment ? "bg-primary" : "bg-muted"
            )}
          >
            <span className={cn(
              "pointer-events-none block h-3 w-3 rounded-full bg-background shadow-lg ring-0 transition-transform",
              useLlmJudgment ? "translate-x-3" : "translate-x-0"
            )} />
          </button>
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="text-sm text-red-500 bg-red-500/10 rounded px-3 py-2">{error}</div>
        )}

        {/* ── Loading ── */}
        {loading && (
          <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            正在分析 {ticker}，{days} 天数据...
          </div>
        )}

        {/* ── Results ── */}
        {result && report && (
          <div className="space-y-4 mt-4">
            {/* Summary */}
            {summary && (
              <div className="flex items-start gap-2 px-3 py-2 rounded-lg border bg-primary/5 text-sm text-muted-foreground">
                <Sparkles size={14} className="text-primary mt-0.5 shrink-0" />
                <p className="leading-relaxed">{summary}</p>
              </div>
            )}

            {/* Consensus */}
            {consensusPicks.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                  <Award size={14} className="text-yellow-500" />
                  大师共识
                </h4>
                <div className="space-y-2">
                  {consensusPicks.map(pick => (
                    <div key={pick.ticker} className="rounded border p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">{pick.ticker}</span>
                        <span className="text-xs text-muted-foreground">
                          {pick.total_analysts} 位分析师
                        </span>
                      </div>
                      <ConsensusScore score={pick.consensus_score} />
                      <div className="flex justify-between text-xs mt-2">
                        <span className="text-green-500">
                          <TrendingUp size={12} className="inline mr-0.5" />
                          看多 {pick.bullish_count}
                        </span>
                        <span className="text-muted-foreground">中性 {pick.neutral_count}</span>
                        <span className="text-red-500">
                          <TrendingDown size={12} className="inline mr-0.5" />
                          看空 {pick.bearish_count}
                        </span>
                      </div>
                      {pick.top_bullish_analysts.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {pick.top_bullish_analysts.map(name => (
                            <span key={name} className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-600">
                              {name}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Win rate leaderboard */}
            {performances.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                  <Brain size={14} className="text-primary" />
                  大师胜率排行（{result.total_days} 天回测）
                </h4>
                <div className="rounded border divide-y">
                  {performances.map((p, i) => (
                    <div key={p.analyst_key} className="flex items-center gap-3 px-3 py-2 text-sm">
                      <span className={cn(
                        'w-5 text-center text-xs font-bold',
                        i === 0 ? 'text-yellow-500' : i === 1 ? 'text-gray-400' : i === 2 ? 'text-amber-600' : 'text-muted-foreground',
                      )}>
                        {i + 1}
                      </span>
                      <span className="w-16 font-medium">{p.analyst_name}</span>
                      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div
                          className={cn('h-full rounded-full', p.win_rate >= 60 ? 'bg-green-500' : p.win_rate >= 40 ? 'bg-yellow-500' : 'bg-red-500')}
                          style={{ width: `${p.win_rate}%` }}
                        />
                      </div>
                      <span className={cn(
                        'w-14 text-right text-xs font-bold',
                        p.win_rate >= 60 ? 'text-green-500' : p.win_rate >= 40 ? 'text-yellow-500' : 'text-red-500',
                      )}>
                        {p.win_rate.toFixed(1)}%
                      </span>
                      <span className="text-xs text-muted-foreground w-16 text-right">
                        {p.correct_predictions}/{p.total_predictions}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
