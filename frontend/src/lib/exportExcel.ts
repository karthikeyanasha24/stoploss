/**
 * Build .xlsx files from API data (full rows/columns — not a screenshot of the visible table).
 */
import * as XLSX from "xlsx";
import type { Analysis, Trade } from "./api";

function cell(v: unknown): string | number | boolean | null {
  if (v === undefined || v === null) return null;
  if (typeof v === "boolean" || typeof v === "number") return v;
  if (typeof v === "string") return v;
  return String(v);
}

/** One row per trade with every field the API returns (wide sheet — no horizontal scroll needed in Excel). */
export function tradesToRows(trades: Trade[]): Record<string, string | number | boolean | null>[] {
  return trades.map((t) => ({
    id: cell(t.id),
    ticker: cell(t.ticker),
    strike_price: cell(t.strike_price),
    option_type: cell(t.option_type),
    expiry_date: cell(t.expiry_date),
    entry_time: cell(t.entry_time),
    entry_price: cell(t.entry_price),
    analyst_name: cell(t.analyst_name),
    status: cell(t.status),
    take_profit_targets: t.take_profit_targets?.length ? t.take_profit_targets.join(", ") : "",
    take_profit_targets_order: t.take_profit_targets_order?.length
      ? t.take_profit_targets_order.join(", ")
      : "",
    lowest_price_before_tp1_manual: cell(t.lowest_price_before_tp1_manual),
    take_profit_target_price: cell(t.take_profit_target_price),
    tp1_upside_percent: cell(t.tp1_upside_percent),
    take_profit_hit_at: cell(t.take_profit_hit_at),
    take_profit_hit_price: cell(t.take_profit_hit_price),
    drawdown_before_take_profit_price: cell(t.drawdown_before_take_profit_price),
    drawdown_before_take_profit_percent: cell(t.drawdown_before_take_profit_percent),
    drawdown_before_tp1_percent_signed: cell(t.drawdown_before_tp1_percent_signed),
    min_before_tp1_source: cell(t.min_before_tp1_source),
    drawdown_price: cell(t.drawdown_price),
    max_drawdown_percent: cell(t.max_drawdown_percent),
    current_price: cell(t.current_price),
    current_price_source: cell(t.current_price_source),
    tp_hit_flag: cell(t.tp_hit_flag),
    lowest_price_before_tp: cell(t.lowest_price_before_tp),
    babji_low_price: cell(t.babji_low_price),
    babji_drawdown_source: cell(t.babji_drawdown_source),
    babji_drawdown_percent: cell(t.babji_drawdown_percent),
    babji_no_pretp_history: cell(t.babji_no_pretp_history),
    lowest_price_at: cell(t.lowest_price_at),
    current_drawdown_percent: cell(t.current_drawdown_percent),
    per_tp_babji_json: t.per_tp_babji?.length ? JSON.stringify(t.per_tp_babji) : "",
  }));
}

export function downloadTradesExcel(trades: Trade[], filenameBase = "dashboard-trades") {
  const rows = tradesToRows(trades);
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Trades");
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  XLSX.writeFile(wb, `${filenameBase}-${stamp}.xlsx`);
}

export function downloadAnalysisExcel(data: Analysis, filenameBase = "stop-loss-analysis") {
  const wb = XLSX.utils.book_new();

  const summaryRows: Record<string, string | number | null>[] = [
    { key: "message", value: cell(data.message) },
    { key: "analysis_days", value: cell(data.analysis_days) },
    { key: "total_trades_analyzed", value: cell(data.total_trades_analyzed) },
    { key: "trades_with_take_profit_hits", value: cell(data.trades_with_take_profit_hits) },
    { key: "skipped_without_take_profit", value: cell(data.skipped_without_take_profit) },
    { key: "skipped_without_take_profit_hit", value: cell(data.skipped_without_take_profit_hit) },
    { key: "excluded_lotto_outliers", value: cell(data.excluded_lotto_outliers) },
    { key: "total_trades_for_stop_simulation", value: cell(data.total_trades_for_stop_simulation) },
    { key: "recommended_stop_pct", value: cell(data.recommended_stop) },
    { key: "summary", value: cell(data.summary) },
  ];
  if (data.excluded_signed_drawdown_threshold_percent != null) {
    summaryRows.push({
      key: "excluded_signed_drawdown_threshold_percent",
      value: cell(data.excluded_signed_drawdown_threshold_percent),
    });
  }
  if (data.drawdown_signed_summary) {
    const s = data.drawdown_signed_summary;
    summaryRows.push(
      { key: "signed_dd_avg", value: cell(s.average_percent) },
      { key: "signed_dd_min", value: cell(s.min_percent) },
      { key: "signed_dd_max", value: cell(s.max_percent) },
      { key: "signed_dd_note", value: cell(s.note) },
    );
  }
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summaryRows), "Summary");

  if (data.stop_results?.length) {
    XLSX.utils.book_append_sheet(
      wb,
      XLSX.utils.json_to_sheet(
        data.stop_results.map((r) => ({
          stop_percent: r.stop_percent,
          trades_stopped: r.trades_stopped,
          total_trades: r.total_trades,
          trades_stopped_out_pct: r.trades_stopped_out_pct,
        })),
      ),
      "Stop levels",
    );
  }

  if (data.trades_detail?.length) {
    XLSX.utils.book_append_sheet(
      wb,
      XLSX.utils.json_to_sheet(
        data.trades_detail.map((r) => ({
          ticker: r.ticker,
          entry_price: r.entry_price,
          tp1_price: r.tp1_price,
          tp1_upside_percent: r.tp1_upside_percent,
          min_price_before_tp1: r.min_price_before_tp1,
          drawdown_percent_signed: r.drawdown_percent_signed,
          drawdown_percent_magnitude: r.drawdown_percent_magnitude,
          min_before_tp1_source: r.min_before_tp1_source,
          excluded_from_stop_analysis: r.excluded_from_stop_analysis ?? false,
        })),
      ),
      "Trades in sample",
    );
  }

  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  XLSX.writeFile(wb, `${filenameBase}-${stamp}.xlsx`);
}
