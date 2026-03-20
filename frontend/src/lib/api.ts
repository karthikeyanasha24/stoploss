const API_BASE = "/api";

export type Trade = {
  id: number;
  ticker: string;
  strike_price: number;
  option_type: string;
  expiry_date: string;
  /** When the trade was entered (ISO timestamp string) */
  entry_time: string;
  entry_price: number;
  analyst_name: string;
  status: string;
  /** Lowest price seen after entry; null if no price data yet */
  drawdown_price?: number | null;
  /** Max drawdown % from tracking; null if no price data yet (used for analysis, not main dashboard display) */
  max_drawdown_percent?: number | null;
  /** Last fetched option price for comparison with broker */
  current_price?: number | null;
  /** "live" = market open / real-time; "last" = market closed / last available (not live) */
  current_price_source?: "live" | "last" | null;
};

export type TradeStats = {
  trade_id: number;
  ticker: string;
  entry_price: number;
  stats: {
    lowest_price: number;
    highest_price: number;
    max_drawdown_percent: number;
  } | null;
};

export type StopResult = {
  stop_percent: number;
  trades_stopped: number;
  total_trades: number;
  trades_stopped_out_pct: number;
};

export type Analysis = {
  analysis_days?: number;
  total_trades_analyzed?: number;
  stop_results: StopResult[];
  recommended_stop: number | null;
  summary?: string;
  message?: string;
};

export async function fetchTrades(): Promise<Trade[]> {
  const r = await fetch(`${API_BASE}/trades`);
  if (!r.ok) throw new Error("Failed to fetch trades");
  return r.json();
}

export async function fetchStats(tradeId: number): Promise<TradeStats> {
  const r = await fetch(`${API_BASE}/stats/${tradeId}`);
  if (!r.ok) throw new Error("Failed to fetch stats");
  return r.json();
}

export async function fetchAnalysis(): Promise<Analysis> {
  const r = await fetch(`${API_BASE}/analysis`);
  if (!r.ok) throw new Error("Failed to fetch analysis");
  return r.json();
}

export async function fetchLogs(): Promise<{ logs: Array<string | { ts?: number; level?: string; name?: string; msg?: string }> }> {
  const r = await fetch(`${API_BASE}/logs`);
  if (!r.ok) throw new Error("Failed to fetch logs");
  return r.json();
}

export type SheetTradeVerbose = {
  ticker_raw: string;
  ticker: string | null;
  strike: number | null;
  option_type: string | null;
  expiry_date: string | null;
  entry_price: number | null;
  status: "on_dashboard" | "expired" | "no_expiry" | "parse_failed" | "invalid_entry" | "futures";
  reason: string;
};

export type SheetReferenceSheet = {
  name: string;
  error?: string;
  skip_reason?: string;
  trades: SheetTradeVerbose[];
};

export type SheetReference = {
  error: string | null;
  sheets: SheetReferenceSheet[];
};

export async function fetchSheetReference(): Promise<SheetReference> {
  const r = await fetch(`${API_BASE}/sheet-reference`);
  if (!r.ok) throw new Error("Failed to fetch sheet reference");
  return r.json();
}

export async function syncSheetToDb(): Promise<{ ok: boolean; added?: number; error?: string }> {
  const r = await fetch(`${API_BASE}/sync`, { method: "POST" });
  return r.json();
}
