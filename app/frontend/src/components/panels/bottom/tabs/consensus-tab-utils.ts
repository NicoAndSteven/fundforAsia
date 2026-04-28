export interface StockConsensus {
  ticker: string;
  totalAnalysts: number;
  bullishCount: number;
  bearishCount: number;
  neutralCount: number;
  consensusScore: number; // -1 to +1
  averageConfidence: number;
  topBullishAnalysts: { name: string; confidence: number }[];
}

export interface AnalystWinRate {
  analystKey: string;
  displayName: string;
  totalPredictions: number;
  correctPredictions: number;
  winRate: number; // 0-100
  recentWinRate: number; // last N predictions
  recentTrend: number; // recentWinRate - winRate
}

export interface SignalMatrixRow {
  ticker: string;
  signals: Record<string, { signal: string; confidence: number }>;
  consensusScore: number;
}

/**
 * Parse a signal value to a normalized string.
 * Handles both string and number confidence fields.
 */
function normalizeSignal(signalData: any): { signal: string; confidence: number } | null {
  if (!signalData) return null;
  const signal = typeof signalData.signal === 'string'
    ? signalData.signal.toUpperCase()
    : 'NEUTRAL';
  const confidence = typeof signalData.confidence === 'number'
    ? signalData.confidence
    : typeof signalData.confidence === 'string'
      ? parseFloat(signalData.confidence) || 0
      : 0;
  return { signal, confidence };
}

/**
 * Calculate stock consensus from analyst_signals.
 * analyst_signals structure: { agent_name: { TICKER: { signal, confidence } } }
 */
export function calculateStockConsensus(analystSignals: Record<string, any>): StockConsensus[] {
  if (!analystSignals || Object.keys(analystSignals).length === 0) return [];

  // Collect signals per ticker across all analysts
  const tickerMap = new Map<string, {
    signals: { analyst: string; signal: string; confidence: number }[];
  }>();

  for (const [agent, tickers] of Object.entries(analystSignals)) {
    if (!tickers || typeof tickers !== 'object') continue;
    for (const [ticker, signalData] of Object.entries(tickers)) {
      const normalized = normalizeSignal(signalData);
      if (!normalized) continue;
      if (!tickerMap.has(ticker)) {
        tickerMap.set(ticker, { signals: [] });
      }
      tickerMap.get(ticker)!.signals.push({
        analyst: agent,
        ...normalized,
      });
    }
  }

  // Calculate consensus for each ticker
  const results: StockConsensus[] = [];
  for (const [ticker, data] of tickerMap.entries()) {
    let bullish = 0, bearish = 0, neutral = 0;
    let totalConfidence = 0;

    const topSignals: { name: string; confidence: number }[] = [];

    for (const s of data.signals) {
      if (s.signal === 'BULLISH') bullish++;
      else if (s.signal === 'BEARISH') bearish++;
      else neutral++;
      totalConfidence += s.confidence;
      if (s.signal === 'BULLISH') {
        topSignals.push({ name: s.analyst, confidence: s.confidence });
      }
    }

    const total = data.signals.length;
    const consensusScore = total > 0 ? (bullish - bearish) / total : 0;
    const averageConfidence = total > 0 ? totalConfidence / total : 0;

    // Sort top bullish analysts by confidence
    topSignals.sort((a, b) => b.confidence - a.confidence);

    results.push({
      ticker,
      totalAnalysts: total,
      bullishCount: bullish,
      bearishCount: bearish,
      neutralCount: neutral,
      consensusScore,
      averageConfidence,
      topBullishAnalysts: topSignals,
    });
  }

  // Sort by consensus score descending (most bullish first)
  results.sort((a, b) => b.consensusScore - a.consensusScore);
  return results;
}

/**
 * Calculate win rates for each analyst from backtest results.
 * Compares analyst signal direction on day N with actual price change on day N+1.
 * Neutrals are not counted (no direction to verify).
 */
export function calculateAnalystWinRate(
  backtestResults: any[],
  recentWindow: number = 10
): AnalystWinRate[] {
  if (!backtestResults || backtestResults.length < 2) return [];

  // Track per-analyst stats
  const stats = new Map<string, {
    total: number;
    correct: number;
    predictions: { correct: boolean }[]; // for recent window calc
  }>();

  for (let i = 0; i < backtestResults.length - 1; i++) {
    const today = backtestResults[i];
    const tomorrow = backtestResults[i + 1];

    const signals = today.analyst_signals;
    const pricesToday = today.current_prices;
    const pricesTomorrow = tomorrow.current_prices;

    if (!signals || !pricesToday || !pricesTomorrow) continue;

    for (const [agent, tickerSignals] of Object.entries(signals)) {
      if (!tickerSignals || typeof tickerSignals !== 'object') continue;
      if (agent === 'risk_manager' || agent === 'portfolio_manager') continue;

      for (const [ticker, signalData] of Object.entries(tickerSignals)) {
        const normalized = normalizeSignal(signalData);
        if (!normalized) continue;
        if (normalized.signal === 'NEUTRAL') continue; // neutral has no direction

        const priceToday = pricesToday[ticker];
        const priceTomorrow = pricesTomorrow[ticker];
        if (typeof priceToday !== 'number' || typeof priceTomorrow !== 'number') continue;
        if (priceToday === 0) continue;

        const priceChange = (priceTomorrow - priceToday) / priceToday;

        const isCorrect =
          (normalized.signal === 'BULLISH' && priceChange > 0) ||
          (normalized.signal === 'BEARISH' && priceChange < 0);

        if (!stats.has(agent)) {
          stats.set(agent, { total: 0, correct: 0, predictions: [] });
        }
        const s = stats.get(agent)!;
        s.total++;
        if (isCorrect) s.correct++;
        s.predictions.push({ correct: isCorrect });
      }
    }
  }

  const results: AnalystWinRate[] = [];
  for (const [analystKey, stat] of stats.entries()) {
    if (stat.total === 0) continue;
    const winRate = (stat.correct / stat.total) * 100;

    // Calculate recent win rate
    const recentPredictions = stat.predictions.slice(-recentWindow);
    const recentCorrect = recentPredictions.filter(p => p.correct).length;
    const recentWinRate = recentPredictions.length > 0
      ? (recentCorrect / recentPredictions.length) * 100
      : winRate;

    results.push({
      analystKey,
      displayName: getAnalystDisplayName(analystKey),
      totalPredictions: stat.total,
      correctPredictions: stat.correct,
      winRate,
      recentWinRate,
      recentTrend: recentWinRate - winRate,
    });
  }

  // Sort by win rate descending
  results.sort((a, b) => b.winRate - a.winRate);
  return results;
}

/**
 * Build signal matrix rows from analyst_signals.
 */
export function buildSignalMatrix(analystSignals: Record<string, any>): {
  rows: SignalMatrixRow[];
  analystKeys: string[];
} {
  if (!analystSignals || Object.keys(analystSignals).length === 0) {
    return { rows: [], analystKeys: [] };
  }

  // Discover all tickers and analysts
  const tickerSet = new Set<string>();
  const analystSet = new Set<string>();

  for (const [agent, tickers] of Object.entries(analystSignals)) {
    if (!tickers || typeof tickers !== 'object') continue;
    analystSet.add(agent);
    for (const ticker of Object.keys(tickers)) {
      tickerSet.add(ticker);
    }
  }

  const analystKeys = Array.from(analystSet).sort();
  const rows: SignalMatrixRow[] = [];

  for (const ticker of tickerSet) {
    const signals: Record<string, { signal: string; confidence: number }> = {};
    let bullish = 0, bearish = 0;

    for (const agent of analystKeys) {
      const signalData = analystSignals[agent]?.[ticker];
      const normalized = normalizeSignal(signalData);
      if (normalized) {
        signals[agent] = normalized;
        if (normalized.signal === 'BULLISH') bullish++;
        else if (normalized.signal === 'BEARISH') bearish++;
      }
    }

    const total = analystKeys.length;
    const consensusScore = total > 0 ? (bullish - bearish) / total : 0;

    rows.push({ ticker, signals, consensusScore });
  }

  // Sort by consensus score descending
  rows.sort((a, b) => b.consensusScore - a.consensusScore);
  return { rows, analystKeys };
}

/**
 * Get a user-friendly display name for an analyst key.
 */
export function getAnalystDisplayName(key: string): string {
  const displayNames: Record<string, string> = {
    warren_buffett: '巴菲特',
    charlie_munger: '芒格',
    ben_graham: '格雷厄姆',
    peter_lynch: '林奇',
    phil_fisher: '费舍',
    bill_ackman: '阿克曼',
    cathie_wood: '伍德',
    michael_burry: '布瑞',
    stanley_druckenmiller: '德鲁肯米勒',
    rakesh_jhunjhunwala: '金君瓦拉',
    nassim_taleb: '塔勒布',
    mohnish_pabrai: '帕布莱',
    aswath_damodaran: '达莫达兰',
    fundamentals_analyst: '基本面',
    technical_analyst: '技术面',
    sentiment_analyst: '情绪面',
    valuation_analyst: '估值面',
    growth_analyst: '成长面',
    news_sentiment_analyst: '新闻情绪',
  };
  return displayNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Get CSS class for win rate bar color.
 */
export function getWinRateColor(winRate: number): string {
  if (winRate >= 70) return 'bg-green-500';
  if (winRate >= 50) return 'bg-yellow-500';
  return 'bg-red-500';
}

/**
 * Get CSS class for win rate text color.
 */
export function getWinRateTextColor(winRate: number): string {
  if (winRate >= 70) return 'text-green-500';
  if (winRate >= 50) return 'text-yellow-500';
  return 'text-red-500';
}

/**
 * Format consensus score to display.
 */
export function formatConsensusScore(score: number): string {
  // Map -1..+1 to 0..100
  const display = Math.round((score + 1) * 50);
  return Math.min(100, Math.max(0, display)).toString();
}
