import { cn } from '@/lib/utils';
import { ChevronUp, ChevronDown, Trophy } from 'lucide-react';
import type { AnalystWinRate } from '../consensus-tab-utils';
import { getWinRateColor, getWinRateTextColor } from '../consensus-tab-utils';

interface AnalystLeaderboardProps {
  analystWinRates: AnalystWinRate[];
  className?: string;
}

export function AnalystLeaderboard({ analystWinRates, className }: AnalystLeaderboardProps) {
  if (!analystWinRates || analystWinRates.length === 0) {
    return null;
  }

  const getRankBadge = (rank: number) => {
    if (rank === 0) return 'text-yellow-500';
    if (rank === 1) return 'text-gray-400';
    if (rank === 2) return 'text-amber-600';
    return 'text-muted-foreground';
  };

  return (
    <div className={cn("rounded-lg border", className)}>
      <div className="flex items-center gap-2 px-4 py-3 border-b bg-muted/30">
        <Trophy size={16} className="text-yellow-500" />
        <h3 className="text-sm font-semibold">分析师胜率排行榜</h3>
        <span className="text-xs text-muted-foreground ml-auto">实时更新</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-xs text-muted-foreground">
              <th className="text-left px-4 py-2 font-medium w-10">#</th>
              <th className="text-left px-4 py-2 font-medium">分析师</th>
              <th className="text-center px-4 py-2 font-medium w-16">正确</th>
              <th className="text-center px-4 py-2 font-medium w-16">总数</th>
              <th className="text-left px-4 py-2 font-medium">胜率</th>
              <th className="text-center px-4 py-2 font-medium w-20">趋势</th>
            </tr>
          </thead>
          <tbody>
            {analystWinRates.map((analyst, index) => {
              const rankColor = getRankBadge(index);
              const barColor = getWinRateColor(analyst.winRate);
              const textColor = getWinRateTextColor(analyst.winRate);
              const showTrend = analyst.recentTrend !== 0;

              return (
                <tr
                  key={analyst.analystKey}
                  className="border-b last:border-b-0 hover:bg-muted/20 transition-colors"
                >
                  <td className={cn("px-4 py-2.5 font-bold", rankColor)}>
                    {index + 1}
                  </td>
                  <td className="px-4 py-2.5 font-medium">
                    {analyst.displayName}
                  </td>
                  <td className="px-4 py-2.5 text-center text-green-500 font-medium">
                    {analyst.correctPredictions}
                  </td>
                  <td className="px-4 py-2.5 text-center text-muted-foreground">
                    {analyst.totalPredictions}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden max-w-[120px]">
                        <div
                          className={cn("h-full rounded-full transition-all duration-500", barColor)}
                          style={{ width: `${Math.min(analyst.winRate, 100)}%` }}
                        />
                      </div>
                      <span className={cn("text-xs font-semibold w-10 text-right", textColor)}>
                        {analyst.winRate.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    {showTrend ? (
                      <div className="flex items-center justify-center gap-1">
                        {analyst.recentTrend > 0 ? (
                          <ChevronUp size={14} className="text-green-500" />
                        ) : (
                          <ChevronDown size={14} className="text-red-500" />
                        )}
                        <span
                          className={cn(
                            "text-xs",
                            analyst.recentTrend > 0 ? 'text-green-500' : 'text-red-500'
                          )}
                        >
                          {analyst.recentTrend > 0 ? '+' : ''}{analyst.recentTrend.toFixed(1)}%
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
