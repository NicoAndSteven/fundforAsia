import { API_BASE_URL } from './api';

export interface IndexData {
  code: string;
  name: string;
  current: number;
  change: number;
  change_pct: number;
  high: number;
  low: number;
  volume: number;
}

export interface SectorData {
  '板块名称': string;
  '涨跌幅': number;
  '上涨家数': number;
  '下跌家数': number;
  '领涨股票': string;
  '总市值': number;
  '成交额': number;
}

export interface MarketBreadth {
  total: number;
  up: number;
  down: number;
  flat: number;
  up_gt_5: number;
  up_3_5: number;
  up_0_3: number;
  down_gt_5: number;
  down_3_5: number;
  down_0_3: number;
  up_ratio: number;
}

export interface StockMoveItem {
  '代码': string;
  '名称': string;
  [key: string]: any;
}

export interface MarketSummary {
  total_volume: number;
  total_volume_str: string;
}

export interface DashboardData {
  indices: IndexData[];
  market_breadth: MarketBreadth;
  sectors: SectorData[];
  top_gainers: StockMoveItem[];
  top_losers: StockMoveItem[];
  top_volume: StockMoveItem[];
  market_summary: MarketSummary;
  limit_up_count: number;
  limit_down_count: number;
  updated_at: string;
  error?: string;
}

export async function fetchDashboard(): Promise<DashboardData> {
  const resp = await fetch(`${API_BASE_URL}/market/dashboard`);
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }
  return resp.json();
}
