import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { StockConsensus } from '../consensus-tab-utils';
import { getAnalystDisplayName, formatConsensusScore } from '../consensus-tab-utils';

interface StockRankerProps {
  stockConsensus: StockConsensus[];
  className?: string;
}

export function StockRanker({ stockConsensus, className }: StockRankerProps) {
  if (!stockConsensus || stockConsensus.length === 0) {
    return null;
  }

  const getScoreBarColor = (score: number) => {
    if (score > 0.3) return 'bg-green-500';
    if (score < -0.3) return 'bg-red-500';
    return 'bg-yellow-500';
  };

  const getSentimentIcon = (score: number) => {
    if (score > 0.3) return <TrendingUp size={14} className="text-green-500" />;
    if (score < -0.3) return <TrendingDown size={14} className="text-red-500" />;
    return <Minus size={14} className="text-muted-foreground" />;
  };

  const getScoreTextClass = (score: number) => {
    if (score > 0.3) return 'text-green-500';
    if (score < -0.3) return 'text-red-500';
    return 'text-muted-foreground';
  };

  return (
    <div className={cn("rounded-lg border", className)}>
      <div className="flex items-center gap-2 px-4 py-3 border-b bg-muted/30">
        <TrendingUp size={16} className="text-primary" />
        <h3 className="text-sm font-semibold">股票共识排行</h3>
        <span className="text-xs text-muted-foreground ml-auto">
          基于 {stockConsensus.length > 0 ? stockConsensus[0].totalAnalysts : 0} 位分析师信号
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-xs text-muted-foreground">
              <th className="text-left px-4 py-2 font-medium w-8">#</th>
              <th className="text-left px-4 py-2 font-medium">股票</th>
              <th className="text-left px-4 py-2 font-medium">共识分</th>
              <th className="text-center px-4 py-2 font-medium w-16 text-green-500">看涨</th>
              <th className="text-center px-4 py-2 font-medium w-16 text-red-500">看跌</th>
              <th className="text-center px-4 py-2 font-medium w-16">中性</th>
              <th className="text-left px-4 py-2 font-medium">最佳分析师</th>
            </tr>
          </thead>
          <tbody>
            {stockConsensus.map((item, index) => {
              const barColor = getScoreBarColor(item.consensusScore);
              const scoreText = getScoreTextClass(item.consensusScore);
              const displayScore = formatConsensusScore(item.consensusScore);

              return (
                <tr
                  key={item.ticker}
                  className="border-b last:border-b-0 hover:bg-muted/20 transition-colors"
                >
                  <td className="px-4 py-2.5 text-muted-foreground font-medium">
                    {index + 1}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="font-semibold">{item.ticker}</span>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden max-w-[100px]">
                        <div
                          className={cn("h-full rounded-full transition-all", barColor)}
                          style={{
                            width: `${displayScore}%`,
                          }}
                        />
                      </div>
                      <div className="flex items-center gap-1 min-w-[40px]">
                        {getSentimentIcon(item.consensusScore)}
                        <span className={cn("text-xs font-semibold", scoreText)}>
                          {displayScore}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span className="text-green-500 font-semibold">{item.bullishCount}</span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span className="text-red-500 font-semibold">{item.bearishCount}</span>
                  </td>
                  <td className="px-4 py-2.5 text-center text-muted-foreground">
                    {item.neutralCount}
                  </td>
                  <td className="px-4 py-2.5">
                    {item.topBullishAnalysts.length > 0 ? (
                      <div className="flex items-center gap-1">
                        <span className="text-xs">
                          {getAnalystDisplayName(item.topBullishAnalysts[0].name)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          ({item.topBullishAnalysts[0].confidence.toFixed(0)}%)
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
