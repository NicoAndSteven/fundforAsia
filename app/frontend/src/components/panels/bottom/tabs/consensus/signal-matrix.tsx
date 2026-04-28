import { cn } from '@/lib/utils';
import type { SignalMatrixRow } from '../consensus-tab-utils';
import { getAnalystDisplayName, formatConsensusScore } from '../consensus-tab-utils';

interface SignalMatrixProps {
  rows: SignalMatrixRow[];
  analystKeys: string[];
  className?: string;
}

export function SignalMatrix({ rows, analystKeys, className }: SignalMatrixProps) {
  if (!rows || rows.length === 0 || !analystKeys || analystKeys.length === 0) {
    return null;
  }

  const getCellStyle = (signal: string) => {
    switch (signal) {
      case 'BULLISH':
        return 'bg-green-500/20 text-green-600 dark:text-green-400 border-green-500/30';
      case 'BEARISH':
        return 'bg-red-500/20 text-red-600 dark:text-red-400 border-red-500/30';
      default:
        return 'bg-muted/40 text-muted-foreground border-muted-foreground/20';
    }
  };

  const getSignalLabel = (signal: string) => {
    switch (signal) {
      case 'BULLISH': return '多';
      case 'BEARISH': return '空';
      default: return '中';
    }
  };

  const getScoreCellColor = (score: number) => {
    if (score > 0.3) return 'text-green-500';
    if (score < -0.3) return 'text-red-500';
    return 'text-muted-foreground';
  };

  return (
    <div className={cn("rounded-lg border", className)}>
      <div className="flex items-center gap-2 px-4 py-3 border-b bg-muted/30">
        <h3 className="text-sm font-semibold">信号矩阵</h3>
        <span className="text-xs text-muted-foreground ml-auto">
          多=看涨 空=看跌 中=中性
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-xs text-muted-foreground">
              <th className="text-left px-3 py-2 font-medium sticky left-0 bg-background z-10 min-w-[70px]">
                股票
              </th>
              {analystKeys.map(key => (
                <th
                  key={key}
                  className="text-center px-2 py-2 font-medium min-w-[48px] max-w-[64px] truncate"
                  title={getAnalystDisplayName(key)}
                >
                  {getAnalystDisplayName(key)}
                </th>
              ))}
              <th className="text-center px-3 py-2 font-medium min-w-[50px]">共识</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr
                key={row.ticker}
                className="border-b last:border-b-0 hover:bg-muted/20 transition-colors"
              >
                <td className="px-3 py-2 font-semibold text-xs sticky left-0 bg-background z-10">
                  {row.ticker}
                </td>
                {analystKeys.map(agent => {
                  const signalData = row.signals[agent];
                  return (
                    <td key={agent} className="px-2 py-2 text-center">
                      {signalData ? (
                        <span
                          className={cn(
                            "inline-flex items-center justify-center w-7 h-7 rounded text-xs font-bold border cursor-default transition-colors",
                            getCellStyle(signalData.signal)
                          )}
                          title={`${getAnalystDisplayName(agent)}: ${signalData.signal} (${signalData.confidence}%)`}
                        >
                          {getSignalLabel(signalData.signal)}
                        </span>
                      ) : (
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded text-xs text-muted-foreground/30">
                          -
                        </span>
                      )}
                    </td>
                  );
                })}
                <td className={cn(
                  "px-3 py-2 text-center font-bold text-xs",
                  getScoreCellColor(row.consensusScore)
                )}>
                  {formatConsensusScore(row.consensusScore)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
