const API_BASE = "/api";

/** Per TP (sheet order): window entry → first touch of that TP; from price_logs on the server. */
export type PerTpBabjiRow = {
  tp_index: number;
  tp_price: number;
  hit_at: string | null;
  babji_low: number | null;
  babji_dd_percent: number | null;
  low_at: string | null;
};

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
  take_profit_targets?: number[];
  /** Exit prices in sheet order (TP1 = first value above entry in this list) */
  take_profit_targets_order?: number[];
  /** Optional: from sheet column "Lowest Price Before TP1" */
  lowest_price_before_tp1_manual?: number | null;
  take_profit_target_price?: number | null;
  tp1_upside_percent?: number | null;
  take_profit_hit_at?: string | null;
  take_profit_hit_price?: number | null;
  drawdown_before_take_profit_price?: number | null;
  /** Positive MAE % for stop simulation: (entry - min) / entry * 100 */
  drawdown_before_take_profit_percent?: number | null;
  /** (min - entry) / entry * 100 — negative when underwater before TP1 */
  drawdown_before_tp1_percent_signed?: number | null;
  min_before_tp1_source?: "manual_sheet" | "price_logs" | null;
  /** Lowest price seen after entry; null if no price data yet */
  drawdown_price?: number | null;
  /** Max drawdown % from tracking; null if no price data yet (used for analysis, not main dashboard display) */
  max_drawdown_percent?: number | null;
  /** Last fetched option price for comparison with broker */
  current_price?: number | null;
  /** "live" = market open / real-time; "last" = market closed / last available (not live) */
  current_price_source?: "live" | "last" | null;
  // ── Babji drawdown fields ──────────────────────────────────────────────────
  /** True when Babji DD is frozen (TP hit or manual min-before-TP from sheet) */
  tp_hit_flag?: boolean;
  /** Lowest premium before first TP (frozen $); null when LIVE/NO_TP use running low instead */
  lowest_price_before_tp?: number | null;
  /** Dollar level Babji DD % is computed from (frozen min before TP, or running low, or last) */
  babji_low_price?: number | null;
  /** How Babji DD was derived */
  /** FROZEN / LIMITED / LIVE when TP1 exists; null when no Take Profits (Babji N/A) */
  babji_drawdown_source?: "FROZEN" | "LIMITED" | "LIVE" | null;
  /**
   * Babji drawdown % — MAE before profitability:
   * FROZEN: entry→lowest before TP1 (manual / price logs / tracker freeze)
   * LIVE: entry→running lowest while TP1 not hit
   * NO_TP: same basis as Current DD % (running low) or entry−last if no stats
   */
  babji_drawdown_percent?: number | null;
  /** True when frozen Babji is 0% only because we never saw a dip before TP in stored data */
  babji_no_pretp_history?: boolean;
  /** Always live: (entry − lowest_seen) / entry × 100 */
  current_drawdown_percent?: number | null;
  /** ISO time when running global low was last updated (tracker); — in UI if unknown */
  lowest_price_at?: string | null;
  per_tp_babji?: PerTpBabjiRow[];
};

export type TradeStats = {
  trade_id: number;
  ticker: string;
  entry_price: number;
  take_profit_targets?: number[];
  stats: {
    lowest_price: number;
    highest_price: number;
    max_drawdown_percent: number;
    current_price?: number | null;
    take_profit_target_price?: number | null;
    take_profit_hit_at?: string | null;
    take_profit_hit_price?: number | null;
    drawdown_before_take_profit_price?: number | null;
    drawdown_before_take_profit_percent?: number | null;
  } | null;
};

export type StopResult = {
  stop_percent: number;
  trades_stopped: number;
  total_trades: number;
  trades_stopped_out_pct: number;
};

export type AnalysisTradeDetail = {
  ticker: string;
  entry_price: number;
  tp1_price: number;
  tp1_upside_percent: number | null;
  min_price_before_tp1: number | null;
  drawdown_percent_signed: number | null;
  drawdown_percent_magnitude: number | null;
  min_before_tp1_source: string | null;
  excluded_from_stop_analysis?: boolean;
};

export type Analysis = {
  analysis_days?: number;
  total_trades_analyzed?: number;
  trades_with_take_profit_hits?: number;
  skipped_without_take_profit?: number;
  skipped_without_take_profit_hit?: number;
  excluded_lotto_outliers?: number;
  excluded_signed_drawdown_threshold_percent?: number;
  total_trades_for_stop_simulation?: number;
  stop_results: StopResult[];
  recommended_stop: number | null;
  recommendation_method?: string;
  recommendation_target_stop_out_pct?: number;
  summary?: string;
  message?: string;
  trades_detail?: AnalysisTradeDetail[];
  drawdown_signed_summary?: {
    average_percent: number | null;
    min_percent: number | null;
    max_percent: number | null;
    average_percent_excluding_outliers?: number | null;
    min_percent_excluding_outliers?: number | null;
    max_percent_excluding_outliers?: number | null;
    note?: string;
    outlier_note?: string;
  } | null;
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
  take_profit_targets?: number[];
  /** Sheet order (TP1 = first); prefer for display when present */
  take_profit_targets_order?: number[];
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
