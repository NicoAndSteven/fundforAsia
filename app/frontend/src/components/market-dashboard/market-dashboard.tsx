import { useEffect, useRef, useState } from 'react';
import { DashboardData, fetchDashboard } from '@/services/market-service';
import * as echarts from 'echarts';
import { cn } from '@/lib/utils';
import { X, RefreshCw, TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';

interface MarketDashboardProps {
  onClose?: () => void;
}

export function MarketDashboard({ onClose }: MarketDashboardProps) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const sectorChartRef = useRef<HTMLDivElement>(null);
  const breadthChartRef = useRef<HTMLDivElement>(null);
  const sectorInstanceRef = useRef<echarts.ECharts | null>(null);
  const breadthInstanceRef = useRef<echarts.ECharts | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadData = async () => {
    try {
      setError(null);
      const result = await fetchDashboard();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  // Auto refresh every 5 minutes
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(loadData, 5 * 60 * 1000);
      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    }
  }, [autoRefresh]);

  // Render ECharts
  useEffect(() => {
    if (!data || !sectorChartRef.current) return;

    // ── Sector Bar Chart ──
    if (sectorChartRef.current) {
      if (sectorInstanceRef.current) sectorInstanceRef.current.dispose();
      const sectors = data.sectors?.slice(0, 20) ?? [];
      const chart = echarts.init(sectorChartRef.current, undefined, { renderer: 'canvas' });
      sectorInstanceRef.current = chart;

      chart.setOption({
        backgroundColor: 'transparent',
        grid: { left: 100, right: 40, top: 10, bottom: 30 },
        xAxis: {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
          axisLabel: { color: '#888', fontSize: 11 },
        },
        yAxis: {
          type: 'category',
          data: sectors.map(s => s['板块名称']).reverse(),
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { color: '#ccc', fontSize: 11 },
        },
        series: [{
          type: 'bar',
          data: sectors.map(s => ({
            value: s['涨跌幅'],
            itemStyle: {
              color: s['涨跌幅'] >= 0
                ? new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: 'rgba(255,50,50,0.1)' },
                    { offset: 1, color: '#ff3333' },
                  ])
                : new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#00d44b' },
                    { offset: 1, color: 'rgba(0,200,50,0.1)' },
                  ]),
              borderRadius: s['涨跌幅'] >= 0 ? [0, 3, 3, 0] : [3, 0, 0, 3],
            },
          })).reverse(),
          barWidth: 14,
          label: {
            show: true,
            position: 'right',
            formatter: (p: any) => `${p.value > 0 ? '+' : ''}${p.value.toFixed(2)}%`,
            color: (p: any) => p.value >= 0 ? '#ff6666' : '#66ddaa',
            fontSize: 11,
          },
          animationDuration: 800,
          animationEasing: 'cubicOut',
        }],
      });

      chart.on('finished', () => {
        chart.resize();
      });
    }

    return () => {
      sectorInstanceRef.current?.dispose();
    };
  }, [data]);

  // Breadth donut chart
  useEffect(() => {
    if (!data?.market_breadth || !breadthChartRef.current) return;

    if (breadthInstanceRef.current) breadthInstanceRef.current.dispose();
    const chart = echarts.init(breadthChartRef.current);
    breadthInstanceRef.current = chart;

    const b = data.market_breadth;
    chart.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'pie',
        radius: ['55%', '80%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: 'rgba(0,0,0,0.3)',
          borderWidth: 2,
        },
        label: { show: false },
        emphasis: { scale: false },
        data: [
          { value: b.up, name: '上涨', itemStyle: { color: '#ff4444' } },
          { value: b.down, name: '下跌', itemStyle: { color: '#00d44b' } },
          { value: b.flat, name: '平盘', itemStyle: { color: '#666' } },
        ],
        animationDuration: 1000,
      }],
    });

    return () => { breadthInstanceRef.current?.dispose(); };
  }, [data]);

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto" />
          <div className="text-cyan-400 text-sm font-mono">加载市场数据...</div>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <div className="text-red-400 text-sm font-mono">数据加载失败</div>
          <div className="text-muted-foreground text-xs">{error}</div>
          <button
            onClick={loadData}
            className="px-4 py-2 text-sm bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/30 transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  const b = data?.market_breadth;
  const indices = data?.indices ?? [];

  return (
    <div className={cn(
      "h-full w-full overflow-auto bg-background",
      "bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950"
    )}>
      {/* Cyberpunk grid background overlay */}
      <div className="fixed inset-0 pointer-events-none" style={{
        backgroundImage: `
          linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
      }} />

      <div className="relative z-10 max-w-[1600px] mx-auto p-4 md:p-6 space-y-6">
        {/* ── Header ── */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 font-mono tracking-wider">
              MARKET PANORAMA
            </h1>
            <div className="h-4 w-px bg-cyan-500/30" />
            <span className="text-xs text-cyan-600 font-mono">
              {data?.updated_at ? new Date(data.updated_at).toLocaleTimeString('zh-CN', { hour12: false }) : '--'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => { setAutoRefresh(!autoRefresh); }}
              className={cn(
                "px-3 py-1.5 text-xs font-mono rounded border transition-colors",
                autoRefresh
                  ? "border-cyan-500/50 text-cyan-400 bg-cyan-500/10"
                  : "border-slate-700 text-slate-500"
              )}
            >
              {autoRefresh ? '● AUTO' : '○ MANUAL'}
            </button>
            <button
              onClick={loadData}
              className="p-1.5 text-cyan-400 hover:text-cyan-300 transition-colors"
              title="刷新"
            >
              <RefreshCw size={16} />
            </button>
            {onClose && (
              <button onClick={onClose} className="p-1.5 text-slate-500 hover:text-white transition-colors">
                <X size={16} />
              </button>
            )}
          </div>
        </div>

        {/* ── Index Cards ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {indices.map(idx => {
            const isUp = idx.change_pct > 0;
            const isDown = idx.change_pct < 0;
            return (
              <div
                key={idx.code}
                className={cn(
                  "relative rounded-lg p-4 border overflow-hidden",
                  "bg-slate-900/60 backdrop-blur-sm",
                  isUp ? "border-red-900/40" : isDown ? "border-green-900/40" : "border-slate-700/50"
                )}
              >
                {/* Glow effect */}
                <div className={cn(
                  "absolute -top-10 -right-10 w-20 h-20 rounded-full opacity-20 blur-2xl",
                  isUp ? "bg-red-500" : isDown ? "bg-green-500" : "bg-slate-500"
                )} />
                <div className="relative">
                  <div className="text-xs text-slate-500 font-mono mb-1">{idx.name}</div>
                  <div className="text-2xl font-bold font-mono text-white">
                    {idx.current.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    {isUp ? (
                      <TrendingUp size={14} className="text-red-400" />
                    ) : isDown ? (
                      <TrendingDown size={14} className="text-green-400" />
                    ) : (
                      <Minus size={14} className="text-slate-500" />
                    )}
                    <span className={cn(
                      "text-sm font-mono",
                      isUp ? "text-red-400" : isDown ? "text-green-400" : "text-slate-500"
                    )}>
                      {idx.change_pct > 0 ? '+' : ''}{idx.change_pct.toFixed(2)}%
                    </span>
                    <span className={cn(
                      "text-xs font-mono",
                      isUp ? "text-red-600" : isDown ? "text-green-600" : "text-slate-600"
                    )}>
                      {idx.change > 0 ? '+' : ''}{idx.change.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Second Row: Breadth + Sector ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Market Breadth */}
          <div className="lg:col-span-1 rounded-lg border border-slate-800 bg-slate-900/40 backdrop-blur-sm p-4">
            <h3 className="text-xs font-mono text-cyan-500/80 mb-3 tracking-wider">MARKET BREADTH</h3>
            <div className="flex items-center gap-6">
              <div ref={breadthChartRef} className="w-28 h-28 flex-shrink-0" />
              <div className="space-y-2 flex-1">
                <div className="flex justify-between text-sm">
                  <span className="text-red-400 font-mono">上涨</span>
                  <span className="text-red-400 font-mono font-bold">{b?.up ?? 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-green-400 font-mono">下跌</span>
                  <span className="text-green-400 font-mono font-bold">{b?.down ?? 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 font-mono">平盘</span>
                  <span className="text-slate-500 font-mono font-bold">{b?.flat ?? 0}</span>
                </div>
                <div className="h-px bg-slate-800 my-2" />
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600 font-mono">涨停</span>
                  <span className="text-red-500 font-mono">{data?.limit_up_count ?? 0}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600 font-mono">跌停</span>
                  <span className="text-green-500 font-mono">{data?.limit_down_count ?? 0}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600 font-mono">上涨占比</span>
                  <span className="text-cyan-400 font-mono">{b?.up_ratio ?? 0}%</span>
                </div>
              </div>
            </div>
            {data?.market_summary && (
              <div className="mt-3 pt-3 border-t border-slate-800 text-xs text-slate-500 font-mono">
                成交额: {data.market_summary.total_volume_str}
              </div>
            )}
          </div>

          {/* Sector Bar Chart */}
          <div className="lg:col-span-2 rounded-lg border border-slate-800 bg-slate-900/40 backdrop-blur-sm p-4">
            <h3 className="text-xs font-mono text-cyan-500/80 mb-3 tracking-wider">SECTOR RANKING</h3>
            <div ref={sectorChartRef} className="w-full" style={{ height: Math.min((data?.sectors?.length ?? 10) * 22 + 40, 400) }} />
          </div>
        </div>

        {/* ── Third Row: Top Movers ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {([
            { title: 'TOP GAINERS', items: data?.top_gainers ?? [], col: '涨跌幅', icon: TrendingUp, color: 'text-red-400' },
            { title: 'TOP LOSERS', items: data?.top_losers ?? [], col: '涨跌幅', icon: TrendingDown, color: 'text-green-400' },
            { title: 'TOP VOLUME', items: data?.top_volume ?? [], col: '成交额', icon: TrendingUp, color: 'text-cyan-400' },
          ] as const).map(section => (
            <div key={section.title} className="rounded-lg border border-slate-800 bg-slate-900/40 backdrop-blur-sm p-4">
              <div className="flex items-center gap-2 mb-3">
                <section.icon size={12} className={section.color} />
                <h3 className="text-xs font-mono text-cyan-500/80 tracking-wider">{section.title}</h3>
              </div>
              <div className="space-y-1">
                {section.items.length === 0 && (
                  <div className="text-xs text-slate-600 font-mono py-4 text-center">暂无数据</div>
                )}
                {section.items.slice(0, 8).map((item, i) => {
                  const val = item[section.col];
                  const isPct = section.col === '涨跌幅';
                  return (
                    <div key={item['代码'] ?? i} className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-slate-800/50 transition-colors">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-600 font-mono w-4">{i + 1}</span>
                        <span className="text-xs text-slate-300 font-mono truncate max-w-[100px]">{item['名称']}</span>
                      </div>
                      <span className={cn(
                        "text-xs font-mono tabular-nums",
                        isPct && val > 0 && "text-red-400",
                        isPct && val < 0 && "text-green-400",
                        !isPct && "text-cyan-400"
                      )}>
                        {isPct ? `${val > 0 ? '+' : ''}${val?.toFixed(2)}%` : val?.toLocaleString('zh-CN')}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* ── Footer Data Attribution ── */}
        <div className="text-center text-xs text-slate-700 font-mono pb-4">
          数据来源: 东方财富  |  每5分钟自动刷新  |  Market Panorama v1.0
        </div>
      </div>
    </div>
  );
}
