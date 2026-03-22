import { useEffect, useState, useMemo, useCallback } from "react";
import { Link } from "react-router-dom";
import { fetchTrades, fetchAnalysis, syncSheetToDb } from "../lib/api";
import type { Trade } from "../lib/api";
import { downloadTradesExcel } from "../lib/exportExcel";

type SortKey =
  | "entry_time"
  | "ticker"
  | "strike_price"
  | "option_type"
  | "expiry_date"
  | "entry_price"
  | "take_profit_target_price"
  | "drawdown_price"
  | "current_price"
  | "analyst_name"
  | "status"
  | "max_drawdown_percent"
  | "babji_drawdown_percent"
  | "babji_low_price"
  | "babji_drawdown_source";
type SortDir = "asc" | "desc";

/** Which metric columns are visible (row data unchanged). */
type ColumnViewMode = "ALL" | "CURRENT" | "BABJI";

const TABLE_COLUMNS: { key: SortKey; label: string; group: "base" | "current" | "babji" }[] = [
  { key: "entry_time", label: "Date", group: "base" },
  { key: "ticker", label: "Ticker", group: "base" },
  { key: "strike_price", label: "Strike", group: "base" },
  { key: "option_type", label: "Type", group: "base" },
  { key: "expiry_date", label: "Expiry", group: "base" },
  { key: "entry_price", label: "Entry", group: "base" },
  { key: "take_profit_target_price", label: "Take Profits", group: "base" },
  { key: "current_price", label: "Current Price", group: "current" },
  { key: "drawdown_price", label: "Drawdown", group: "current" },
  { key: "max_drawdown_percent", label: "Current DD %", group: "current" },
  { key: "babji_drawdown_percent", label: "Babji DD %", group: "babji" },
  { key: "babji_low_price", label: "Babji Low", group: "babji" },
  { key: "babji_drawdown_source", label: "Source", group: "babji" },
  { key: "analyst_name", label: "Analyst", group: "base" },
  { key: "status", label: "Status", group: "base" },
];

function filterVisibleTableColumns(mode: ColumnViewMode) {
  const showCurrent = mode === "ALL" || mode === "CURRENT";
  const showBabji = mode === "ALL" || mode === "BABJI";
  return TABLE_COLUMNS.filter((c) => {
    if (c.group === "current") return showCurrent;
    if (c.group === "babji") return showBabji;
    return true;
  });
}

const PAGE_SIZE = 10;

function formatCurrency(value: number | null | undefined) {
  return value != null ? `$${value.toFixed(2)}` : "—";
}

function formatEntryDate(value: string | undefined) {
  return value ? new Date(value).toLocaleDateString() : "—";
}

function formatTakeProfitTargets(targets: number[] | undefined, order?: number[] | undefined) {
  const list = order?.length ? order : targets;
  if (!list?.length) {
    return "No TP levels ";
  }
  return list.map((target, i) => `TP${i + 1}: $${target.toFixed(2)}`).join(" · ");
}

/** Date/time for an ISO timestamp, or em dash when unknown / never happened */
function formatIsoDateShort(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function PerTpBabjiDetail({ trade }: { trade: Trade }) {
  const rows = trade.per_tp_babji;
  if (!rows?.length) return null;
  return (
    <ul className="mt-1.5 space-y-0.5 border-t border-border/40 pt-1.5 text-[10px] leading-snug text-muted-foreground">
      {rows.map((row) => (
        <li key={row.tp_index}>
          <span className="font-medium text-foreground/80">TP{row.tp_index}</span> @ ${row.tp_price.toFixed(2)}: DD{" "}
          {row.babji_dd_percent != null ? `${row.babji_dd_percent.toFixed(1)}%` : "—"} · low{" "}
          {row.babji_low != null ? formatCurrency(row.babji_low) : "—"} · low @ {formatIsoDateShort(row.low_at)} · hit @{" "}
          {formatIsoDateShort(row.hit_at)}
        </li>
      ))}
    </ul>
  );
}

function formatBabjiSource(s: Trade["babji_drawdown_source"]) {
  if (s === "FROZEN") return "Frozen";
  if (s === "LIMITED") return "Limited";
  if (s === "LIVE") return "Live";
  return "—";
}

/** First time TP1 was touched (ISO), from API merge or per-TP log scan; — if not yet. */
function getBabjiTp1HitAt(t: Trade): string | null {
  return t.take_profit_hit_at ?? t.per_tp_babji?.[0]?.hit_at ?? null;
}

/** When the Babji low (TP1 window) occurred: TP1 row from logs, else global running-low time from tracker. */
function getBabjiLowAt(t: Trade): string | null {
  return t.per_tp_babji?.[0]?.low_at ?? t.lowest_price_at ?? null;
}

/** When API predates `babji_drawdown_source`, infer from other fields (TP1 targets come from sheet sync). */
function deriveBabjiSource(t: Trade): Trade["babji_drawdown_source"] {
  if (t.babji_drawdown_source) return t.babji_drawdown_source;
  if (t.babji_no_pretp_history) return "LIMITED";
  if (t.babji_drawdown_percent == null) return null;
  if (t.tp_hit_flag) return "FROZEN";
  if ((t.take_profit_targets?.length ?? 0) > 0) return "LIVE";
  return null;
}

function babjiAccentClass(t: Trade): string {
  const s = deriveBabjiSource(t);
  if (s === "FROZEN") return "text-success";
  if (s === "LIMITED") return "text-amber-600 dark:text-amber-400";
  return "text-danger";
}

/** Babji only applies when sheet defines a TP1 (same idea as backend `first_tp1_chronological`). */
function isBabjiApplicable(t: Trade): boolean {
  return t.take_profit_target_price != null;
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 animate-pulse">
      <div className="h-4 w-24 rounded bg-muted mb-3" />
      <div className="h-8 w-16 rounded bg-muted" />
    </div>
  );
}

function SkeletonRow({ columnCount }: { columnCount: number }) {
  return (
    <tr className="border-b border-border">
      {Array.from({ length: columnCount }).map((_, i) => (
        <td key={i} className="px-2 py-2 sm:px-3 sm:py-2.5">
          <div className="h-4 rounded bg-muted animate-pulse" />
        </td>
      ))}
    </tr>
  );
}

function MobileTradeCard({
  trade,
  showCurrentCols,
  showBabjiCols,
}: {
  trade: Trade;
  showCurrentCols: boolean;
  showBabjiCols: boolean;
}) {
  const hasDrawdownData = trade.drawdown_price != null;
  const takeProfitDrawdownPrice = trade.drawdown_before_take_profit_price;
  const takeProfitDrawdownPercent = trade.drawdown_before_take_profit_percent;
  const drawdownLabel = takeProfitDrawdownPercent != null ? "DD to 1st TP" : "Live drawdown";
  const babjiPct = trade.babji_drawdown_percent;
  const babjiLabel = "Babji DD %";

  return (
    <div
      className={`rounded-xl border bg-card p-4 shadow-sm ${
        hasDrawdownData
          ? "border-border"
          : "border-amber-500/30 bg-amber-500/5 dark:bg-amber-900/10"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {formatEntryDate(trade.entry_time)}
          </p>
          <Link
            to={`/trade/${trade.id}`}
            className="mt-1 inline-flex text-lg font-semibold text-accent hover:underline"
          >
            {trade.ticker}
          </Link>
        </div>
        <span
          className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
            trade.option_type === "CALL"
              ? "bg-success/15 text-success"
              : "bg-danger/15 text-danger"
          }`}
        >
          {trade.option_type}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-lg bg-muted/30 p-3">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Strike</p>
          <p className="mt-1 font-medium text-foreground">{trade.strike_price}</p>
        </div>
        <div className="rounded-lg bg-muted/30 p-3">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Expiry</p>
          <p className="mt-1 font-medium text-foreground">{trade.expiry_date}</p>
        </div>
        <div className="rounded-lg bg-muted/30 p-3">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Entry</p>
          <p className="mt-1 font-medium text-foreground">{formatCurrency(trade.entry_price)}</p>
        </div>
        <div className="rounded-lg bg-muted/30 p-3 col-span-2">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Take profits</p>
          <p className="mt-1 font-medium text-foreground">
            {formatTakeProfitTargets(trade.take_profit_targets, trade.take_profit_targets_order)}
          </p>
          <PerTpBabjiDetail trade={trade} />
        </div>
        {showCurrentCols ? (
          <>
            <div className="rounded-lg bg-muted/30 p-3">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Current</p>
              <p className="mt-1 font-medium text-foreground">
                {trade.current_price_source === "last" && trade.current_price != null
                  ? `Last: ${trade.current_price.toFixed(2)}`
                  : formatCurrency(trade.current_price)}
              </p>
            </div>
            <div className="rounded-lg bg-muted/30 p-3">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">{drawdownLabel}</p>
              <p className="mt-1 font-medium text-danger">
                {takeProfitDrawdownPrice != null
                  ? formatCurrency(takeProfitDrawdownPrice)
                  : hasDrawdownData
                    ? formatCurrency(trade.drawdown_price)
                    : "No data"}
              </p>
            </div>
            <div className="rounded-lg bg-muted/30 p-3">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">{drawdownLabel} %</p>
              <p className="mt-1 font-medium text-danger">
                {takeProfitDrawdownPercent != null
                  ? `${takeProfitDrawdownPercent.toFixed(1)}%`
                  : trade.max_drawdown_percent != null
                    ? `${trade.max_drawdown_percent.toFixed(1)}%`
                    : "No data"}
              </p>
            </div>
          </>
        ) : null}
        {showBabjiCols ? (
        <div
          className={`rounded-lg p-3 col-span-2 ${
            !isBabjiApplicable(trade)
              ? "bg-muted/30"
              : deriveBabjiSource(trade) === "FROZEN"
                ? "bg-success/10 border border-success/20"
                : deriveBabjiSource(trade) === "LIMITED"
                  ? "bg-amber-500/10 border border-amber-500/30"
                  : "bg-muted/30"
          }`}
        >
          <p className="text-xs uppercase tracking-wide text-muted-foreground">{babjiLabel}</p>
          {!isBabjiApplicable(trade) ? (
            <p className="mt-1 text-sm text-muted-foreground" title="Babji measures drawdown before TP1 — add Take Profits on the sheet">
              N/A
            </p>
          ) : (
            <>
              <div className="mt-1 flex flex-wrap items-center gap-2">
                <span className={`font-semibold ${babjiAccentClass(trade)}`}>
                  {babjiPct != null ? `${babjiPct.toFixed(1)}%` : "No data"}
                </span>
                <span className="text-xs font-medium text-muted-foreground">
                  {formatBabjiSource(deriveBabjiSource(trade))}
                </span>
              </div>
              <p className="mt-1 space-y-0.5 text-[10px] leading-snug text-muted-foreground">
                <span className="block">
                  TP1 hit {formatIsoDateShort(getBabjiTp1HitAt(trade))}
                </span>
                <span className="block">
                  Low @ {formatIsoDateShort(getBabjiLowAt(trade))}
                </span>
              </p>
              {trade.babji_low_price != null && (
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Babji low: {formatCurrency(trade.babji_low_price)}
                </p>
              )}
            </>
          )}
        </div>
        ) : null}
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-border pt-3 text-sm">
        <p className="min-w-0 text-muted-foreground">
          Analyst: <span className="font-medium text-foreground">{trade.analyst_name || "—"}</span>
        </p>
        <span className="capitalize text-muted-foreground">{trade.status || "—"}</span>
      </div>
    </div>
  );
}

function renderTradeTableCell(
  t: Trade,
  colKey: SortKey,
  ctx: {
    hasDrawdownData: boolean;
    dd: number | null | undefined;
    babjiSrc: ReturnType<typeof deriveBabjiSource>;
  }
) {
  const { hasDrawdownData, dd, babjiSrc } = ctx;
  switch (colKey) {
    case "entry_time":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 text-muted-foreground">
          {formatEntryDate(t.entry_time)}
        </td>
      );
    case "ticker":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 font-medium">
          <Link to={`/trade/${t.id}`} className="text-accent hover:underline">
            {t.ticker}
          </Link>
        </td>
      );
    case "strike_price":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 text-foreground">
          {t.strike_price}
        </td>
      );
    case "option_type":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5">
          <span
            className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
              t.option_type === "CALL"
                ? "bg-success/15 text-success"
                : "bg-danger/15 text-danger"
            }`}
          >
            {t.option_type}
          </span>
        </td>
      );
    case "expiry_date":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 text-muted-foreground">
          {t.expiry_date}
        </td>
      );
    case "entry_price":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 text-foreground">
          {formatCurrency(t.entry_price)}
        </td>
      );
    case "take_profit_target_price":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 text-muted-foreground align-top">
          <div className="min-w-0 max-w-[14rem] sm:max-w-[min(100%,18rem)] break-words">
            <div>{formatTakeProfitTargets(t.take_profit_targets, t.take_profit_targets_order)}</div>
            <PerTpBabjiDetail trade={t} />
          </div>
        </td>
      );
    case "current_price":
      return (
        <td
          key={colKey}
          className="px-2 py-2 sm:px-3 sm:py-2.5"
          title={
            t.current_price_source === "last"
              ? "Last price (not live) — compare with your broker"
              : "Live price — compare with your broker"
          }
        >
          {t.current_price != null ? (
            t.current_price_source === "live" ? (
              <span className="font-medium text-foreground">{formatCurrency(t.current_price)}</span>
            ) : (
              <span className="font-medium text-muted-foreground">Last: {formatCurrency(t.current_price)}</span>
            )
          ) : (
            <span className="text-amber-600 dark:text-amber-400 text-xs font-medium">—</span>
          )}
        </td>
      );
    case "drawdown_price":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5">
          {t.drawdown_before_take_profit_price != null ? (
            <span className="font-medium text-danger">
              {formatCurrency(t.drawdown_before_take_profit_price)}
            </span>
          ) : hasDrawdownData ? (
            <span className="font-medium text-danger">{formatCurrency(dd)}</span>
          ) : (
            <span
              className="text-amber-600 dark:text-amber-400 text-xs font-medium"
              title="No price data yet — tracker may have API issues or market closed"
            >
              No data
            </span>
          )}
        </td>
      );
    case "max_drawdown_percent": {
      const ddTooltip = [
        t.drawdown_before_tp1_percent_signed != null
          ? `MAE ${t.drawdown_before_take_profit_percent?.toFixed(1)}% · signed (min−entry)/entry: ${t.drawdown_before_tp1_percent_signed.toFixed(1)}%`
          : null,
        t.lowest_price_at
          ? `Global running low last seen: ${formatIsoDateShort(t.lowest_price_at)}`
          : null,
      ]
        .filter(Boolean)
        .join(" · ");
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5" title={ddTooltip || undefined}>
          {t.drawdown_before_take_profit_percent != null ? (
            <span className="font-medium text-danger">
              {t.drawdown_before_take_profit_percent.toFixed(1)}%
              {t.drawdown_before_tp1_percent_signed != null ? (
                <span className="block text-xs font-normal text-muted-foreground">
                  signed {t.drawdown_before_tp1_percent_signed.toFixed(1)}%
                </span>
              ) : null}
            </span>
          ) : t.max_drawdown_percent != null ? (
            <span className={t.max_drawdown_percent > 0 ? "font-medium text-danger" : "text-muted-foreground"}>
              {t.max_drawdown_percent.toFixed(1)}%
            </span>
          ) : (
            <span className="text-amber-600 dark:text-amber-400 text-xs font-medium">No data</span>
          )}
        </td>
      );
    }
    case "babji_drawdown_percent":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5">
          {!isBabjiApplicable(t) ? (
            <span className="text-muted-foreground text-xs" title="No TP1 from Take Profits — Babji not applicable">
              N/A
            </span>
          ) : t.babji_drawdown_percent != null ? (
            <span className={`font-semibold ${babjiAccentClass(t)}`}>
              {t.babji_drawdown_percent.toFixed(1)}%
              {babjiSrc === "LIMITED" ? (
                <span
                  className="block text-xs font-normal text-amber-600 dark:text-amber-400"
                  title='TP1 reached in data but no dip observed before TP in stored quotes — add history or use sheet &quot;Lowest before TP1&quot; column'
                >
                  ⚠ limited history
                </span>
              ) : null}
            </span>
          ) : (
            <span className="text-amber-600 dark:text-amber-400 text-xs font-medium">No data</span>
          )}
        </td>
      );
    case "babji_low_price":
      return (
        <td
          key={colKey}
          className="px-2 py-2 sm:px-3 sm:py-2.5 text-foreground"
          title={
            !isBabjiApplicable(t)
              ? "Babji low only when TP1 exists (Take Profits)"
              : babjiSrc === "FROZEN" || babjiSrc === "LIMITED"
                ? "Lowest premium before TP1 (Babji window ends when TP1 is first hit)"
                : babjiSrc === "LIVE"
                  ? "Running lowest since entry while TP1 not yet hit (same window idea as Babji until TP1)"
                  : "—"
          }
        >
          {!isBabjiApplicable(t) ? (
            <span className="text-muted-foreground text-xs">N/A</span>
          ) : t.babji_low_price != null ? (
            <div>
              <span>{formatCurrency(t.babji_low_price)}</span>
              {getBabjiLowAt(t) ? (
                <span className="mt-0.5 block text-[10px] text-muted-foreground" title="When this low was observed (TP1 window or running low)">
                  {formatIsoDateShort(getBabjiLowAt(t))}
                </span>
              ) : null}
            </div>
          ) : (
            "—"
          )}
        </td>
      );
    case "babji_drawdown_source":
      return (
        <td
          key={colKey}
          className="px-2 py-2 sm:px-3 sm:py-2.5 align-top text-muted-foreground text-xs"
          title="TP1 hit = first time price reached TP1. Low = when the Babji low premium occurred (from logs or tracker)."
        >
          {!isBabjiApplicable(t) ? (
            <span className="text-muted-foreground">N/A</span>
          ) : (
            <div className="min-w-0 max-w-[9rem] sm:max-w-[11rem] space-y-1 break-words">
              <div className="font-medium text-foreground">{formatBabjiSource(babjiSrc)}</div>
              <div className="space-y-0.5 text-[10px] leading-snug">
                <div>
                  <span className="text-muted-foreground">TP1 hit </span>
                  {formatIsoDateShort(getBabjiTp1HitAt(t))}
                </div>
                <div>
                  <span className="text-muted-foreground">Babji low </span>
                  {formatIsoDateShort(getBabjiLowAt(t))}
                </div>
              </div>
            </div>
          )}
        </td>
      );
    case "analyst_name":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5 text-muted-foreground">
          {t.analyst_name || "—"}
        </td>
      );
    case "status":
      return (
        <td key={colKey} className="px-2 py-2 sm:px-3 sm:py-2.5">
          <span className="text-sm text-muted-foreground capitalize">{t.status || "—"}</span>
        </td>
      );
    default: {
      const _exhaustive: never = colKey;
      return _exhaustive;
    }
  }
}

export default function Dashboard() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [tradesReady, setTradesReady] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("expiry_date");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(0);
  const [filterPreset, setFilterPreset] = useState<"all" | "today" | "last2" | "last3" | "last7" | "range">("all");
  const [rangeFrom, setRangeFrom] = useState<string>("");
  const [rangeTo, setRangeTo] = useState<string>("");
  const [syncing, setSyncing] = useState(false);
  const [columnView, setColumnView] = useState<ColumnViewMode>("ALL");

  const load = useCallback(async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
      setError(null);
    }
    try {
      const [tradesData, analysisData] = await Promise.all([fetchTrades(), fetchAnalysis()]);
      setTrades(tradesData);
      setTradesReady(analysisData.total_trades_analyzed ?? 0);
      setLastUpdate(new Date());
    } catch (e) {
      if (showLoading) setError(e instanceof Error ? e.message : "Failed to load trades");
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const onSettingsSaved = () => load();
    window.addEventListener("settings-saved", onSettingsSaved);
    return () => window.removeEventListener("settings-saved", onSettingsSaved);
  }, [load]);

  // Auto-refresh every 30s: live sheet data + live API prices
  useEffect(() => {
    const interval = setInterval(() => load(false), 30000);
    return () => clearInterval(interval);
  }, [load]);

  async function handleSyncFromSheet() {
    setSyncing(true);
    setError(null);
    try {
      const res = await syncSheetToDb();
      if (res.ok) {
        await load();
      } else {
        setError(res.error ?? "Sync failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  }

  const filteredTrades = useMemo(() => {
    if (filterPreset === "all") return trades;

    const today = new Date();
    const todayIso = today.toISOString().slice(0, 10);

    function entryDateIso(t: Trade): string | null {
      if (!t.entry_time) return null;
      const d = new Date(t.entry_time);
      if (Number.isNaN(d.getTime())) return null;
      return d.toISOString().slice(0, 10);
    }

    if (filterPreset === "today") {
      return trades.filter((t) => entryDateIso(t) === todayIso);
    }

    if (filterPreset === "last2" || filterPreset === "last3" || filterPreset === "last7") {
      const days = { last2: 2, last3: 3, last7: 7 }[filterPreset];
      const cutoff = new Date();
      // Include today plus previous (days-1) days
      cutoff.setDate(today.getDate() - (days - 1));
      const cutoffIso = cutoff.toISOString().slice(0, 10);
      return trades.filter((t) => {
        const dIso = entryDateIso(t);
        return dIso !== null && dIso >= cutoffIso;
      });
    }

    // Custom range filter (rangeFrom / rangeTo are yyyy-mm-dd)
    if (filterPreset === "range") {
      if (!rangeFrom && !rangeTo) return trades;
      return trades.filter((t) => {
        const dIso = entryDateIso(t);
        if (dIso === null) return false;
        if (rangeFrom && dIso < rangeFrom) return false;
        if (rangeTo && dIso > rangeTo) return false;
        return true;
      });
    }

    return trades;
  }, [trades, filterPreset, rangeFrom, rangeTo]);

  const sortedTrades = useMemo(() => {
    const arr = [...filteredTrades];
    arr.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (
        sortKey === "max_drawdown_percent"
        || sortKey === "current_price"
        || sortKey === "take_profit_target_price"
      ) {
        const aNum = aVal != null ? Number(aVal) : -1;
        const bNum = bVal != null ? Number(bVal) : -1;
        return sortDir === "asc" ? aNum - bNum : bNum - aNum;
      }
      if (sortKey === "babji_drawdown_percent" || sortKey === "babji_low_price") {
        const aNum = aVal != null ? Number(aVal) : -1;
        const bNum = bVal != null ? Number(bVal) : -1;
        return sortDir === "asc" ? aNum - bNum : bNum - aNum;
      }
      if (sortKey === "babji_drawdown_source") {
        const astr = String(deriveBabjiSource(a) ?? "");
        const bstr = String(deriveBabjiSource(b) ?? "");
        return sortDir === "asc" ? astr.localeCompare(bstr) : bstr.localeCompare(astr);
      }
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDir === "asc" ? aVal - bVal : bVal - aVal;
      }
      return 0;
    });
    return arr;
  }, [filteredTrades, sortKey, sortDir]);

  const visibleTableColumns = useMemo(
    () => filterVisibleTableColumns(columnView),
    [columnView]
  );
  const showCurrentCols = columnView === "ALL" || columnView === "CURRENT";
  const showBabjiCols = columnView === "ALL" || columnView === "BABJI";
  const tableColumnCount = visibleTableColumns.length;

  const totalPages = Math.ceil(sortedTrades.length / PAGE_SIZE) || 1;
  const paginatedTrades = sortedTrades.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  useEffect(() => {
    setPage((current) => Math.min(current, Math.max(totalPages - 1, 0)));
  }, [totalPages]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  function handleExportExcel(mode: "filtered" | "all") {
    const list = mode === "filtered" ? sortedTrades : trades;
    if (!list.length) {
      window.alert(
        mode === "filtered"
          ? "No trades match the current filter — change filters or use “Export all trades”."
          : "No trades loaded — sync from the sheet first.",
      );
      return;
    }
    const suffix = mode === "filtered" ? "dashboard-filtered" : "dashboard-all-trades";
    downloadTradesExcel(list, suffix);
  }

  const tradesTracked = trades.filter((t) => t.status?.toLowerCase() === "tracking" || t.status === "active").length || trades.length;

  return (
      <div className="space-y-6 sm:space-y-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Monitor tracked trades and performance
          </p>
        </div>
        <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center sm:flex-wrap">
        <div className="flex w-full flex-col gap-1 sm:w-auto">
          <button
            type="button"
            onClick={() => handleExportExcel("filtered")}
            disabled={loading}
            className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-muted/50 disabled:opacity-50"
            title="Downloads an Excel file with every column and every row matching your current filters and sort (not only the current page). No horizontal scrolling needed."
          >
            <svg className="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export to Excel
          </button>
          <button
            type="button"
            onClick={() => handleExportExcel("all")}
            disabled={loading || trades.length === 0}
            className="inline-flex w-full sm:w-auto items-center justify-center rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 disabled:opacity-50"
            title="Same full columns, but every trade in the app (ignores date filters)."
          >
            Export all trades (ignore filters)
          </button>
        </div>
        <button
          type="button"
          onClick={() => window.print()}
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg border border-border bg-muted/30 px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-muted/50 print:hidden"
          title="Opens your browser’s print dialog — choose Save as PDF to capture the full page. For very wide tables, pick Landscape in the print dialog."
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Print / Save PDF
        </button>
        <button
          type="button"
          onClick={handleSyncFromSheet}
          disabled={syncing || loading}
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-muted/50 disabled:opacity-50"
        >
          {syncing ? (
            "Syncing…"
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Sync from Sheet
            </>
          )}
        </button>
        </div>
      </div>
      {trades.length === 0 && !loading && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm">
          <p className="font-medium text-amber-700 dark:text-amber-400">No trades yet</p>
          <p className="mt-1 text-muted-foreground">
            Click &quot;Sync from Sheet&quot; above to load trades from your Google Sheet. Or check{" "}
            <Link to="/sheet-reference" className="text-accent hover:underline">Sheet Reference</Link> to verify the sheet connection.
          </p>
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-colors sm:p-6">
              <p className="text-sm font-medium text-muted-foreground">Total Active Trades</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{trades.length}</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-colors sm:p-6">
              <p className="text-sm font-medium text-muted-foreground">Trades Being Tracked</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{tradesTracked}</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-colors sm:p-6">
              <p className="text-sm font-medium text-muted-foreground">Trades Ready for Analysis</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{tradesReady}</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-colors sm:p-6">
              <p className="text-sm font-medium text-muted-foreground">Last Update</p>
              <p className="mt-2 text-lg font-medium text-foreground">
                {lastUpdate ? lastUpdate.toLocaleTimeString() : "—"}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">Auto-refreshes every 30s</p>
            </div>
          </>
        )}
      </div>

      {/* Active Trades Table — id for print; wide layout + compact cells reduce horizontal scroll */}
      <div
        id="dashboard-active-trades"
        className="overflow-hidden rounded-xl border border-border bg-card shadow-sm print:shadow-none print:border-border"
      >
        <div className="px-4 sm:px-6 py-4 border-b border-border flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Active Trades</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {loading
                ? "Loading…"
                : `${filteredTrades.length} trade${filteredTrades.length === 1 ? "" : "s"} shown`}
              {!loading && trades.length > 0 && (
                <>
                  {" "}
                  —{" "}
                  <span className="text-amber-600 dark:text-amber-400">
                    Babji DD applies only when Take Profits define TP1 — no TP column means N/A (use Current DD %). When TP exists: Live (before TP1), Frozen/Limited (after TP1). Current DD %: global low since tracking. Amber: no price yet.
                  </span>
                </>
              )}
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:items-end">
            <button
              type="button"
              onClick={handleSyncFromSheet}
              disabled={syncing || loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-accent/50 bg-accent/10 px-3 py-2 text-sm font-medium text-accent hover:bg-accent/20 disabled:opacity-50 sm:w-auto sm:py-1.5"
            >
              {syncing ? (
                "Syncing…"
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Sync from Sheet
                </>
              )}
            </button>
            {/* Filter presets — horizontally scrollable on mobile */}
            <div className="w-full overflow-x-auto pb-0.5 sm:w-auto">
              <div className="inline-flex min-w-max rounded-lg border border-border bg-muted/40 p-0.5 text-xs sm:text-sm">
                <button
                  type="button"
                  onClick={() => {
                    setFilterPreset("all");
                    setPage(0);
                  }}
                  className={`px-3 py-1.5 rounded-md font-medium transition-colors whitespace-nowrap ${
                    filterPreset === "all" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  All
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setFilterPreset("today");
                    setPage(0);
                  }}
                  className={`px-3 py-1.5 rounded-md font-medium transition-colors whitespace-nowrap ${
                    filterPreset === "today"
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Today
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setFilterPreset("last2");
                    setPage(0);
                  }}
                  className={`px-3 py-1.5 rounded-md font-medium transition-colors whitespace-nowrap ${
                    filterPreset === "last2"
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Last 2 days
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setFilterPreset("last3");
                    setPage(0);
                  }}
                  className={`px-3 py-1.5 rounded-md font-medium transition-colors whitespace-nowrap ${
                    filterPreset === "last3"
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Last 3 days
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setFilterPreset("last7");
                    setPage(0);
                  }}
                  className={`px-3 py-1.5 rounded-md font-medium transition-colors whitespace-nowrap ${
                    filterPreset === "last7"
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Last 7 days
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 gap-2 text-xs sm:flex sm:flex-wrap sm:items-center sm:text-sm">
              <span className="text-muted-foreground">Custom range:</span>
              <input
                type="date"
                value={rangeFrom}
                onChange={(e) => {
                  setRangeFrom(e.target.value);
                  setFilterPreset("range");
                  setPage(0);
                }}
                className="w-full rounded-md border border-border bg-background px-2 py-1 text-xs sm:w-auto sm:text-sm"
              />
              <span className="text-muted-foreground">to</span>
              <input
                type="date"
                value={rangeTo}
                onChange={(e) => {
                  setRangeTo(e.target.value);
                  setFilterPreset("range");
                  setPage(0);
                }}
                className="w-full rounded-md border border-border bg-background px-2 py-1 text-xs sm:w-auto sm:text-sm"
              />
              {(rangeFrom || rangeTo) && (
                <button
                  type="button"
                  onClick={() => {
                    setRangeFrom("");
                    setRangeTo("");
                    setFilterPreset("all");
                    setPage(0);
                  }}
                  className="text-xs text-accent hover:underline"
                >
                  Clear
                </button>
              )}
            </div>
            {/* Column visibility (not row filter): All = show Current + Babji metric columns; Current/Babji = one group only */}
            <div className="w-full flex flex-wrap items-center justify-end gap-2 pt-1">
              <span className="text-xs text-muted-foreground shrink-0">Columns</span>
              <div className="inline-flex rounded-lg border border-border bg-muted/40 p-0.5 text-xs">
                {(["ALL", "CURRENT", "BABJI"] as const).map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setColumnView(m)}
                    aria-pressed={columnView === m}
                    className={`px-2.5 py-1 rounded-md font-medium whitespace-nowrap transition-colors ${
                      columnView === m
                        ? "bg-card text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {m === "ALL" ? "All" : m === "CURRENT" ? "Current" : "Babji"}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mx-6 mt-4 rounded-lg bg-danger/10 border border-danger/20 px-2 py-2 sm:px-3 sm:py-2.5 text-danger text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4 p-4 sm:hidden">
          {loading
            ? Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-border bg-card p-4">
                  <div className="h-5 w-24 animate-pulse rounded bg-muted" />
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {Array.from({ length: 6 }).map((__, idx) => (
                      <div key={idx} className="h-16 animate-pulse rounded-lg bg-muted/70" />
                    ))}
                  </div>
                </div>
              ))
            : paginatedTrades.map((trade) => (
                <MobileTradeCard
                  key={trade.id}
                  trade={trade}
                  showCurrentCols={showCurrentCols}
                  showBabjiCols={showBabjiCols}
                />
              ))}
        </div>

        <div className="hidden w-full min-w-0 overflow-x-auto sm:block print:overflow-visible">
          <table className="w-full min-w-0 table-auto text-xs print:text-[11px]">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                {visibleTableColumns.map((col) => (
                  <th
                    key={col.key}
                    className="px-2 py-2 sm:px-3 sm:py-2.5 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort(col.key)}
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      {sortKey === col.key && (
                        <span className="text-accent">{sortDir === "asc" ? "↑" : "↓"}</span>
                      )}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <SkeletonRow key={i} columnCount={tableColumnCount} />
                  ))
                : paginatedTrades.map((t) => {
                    const hasDrawdownData = t.drawdown_price != null;
                    const dd = t.drawdown_price;
                    const babjiSrc = deriveBabjiSource(t);
                    const ctx = { hasDrawdownData, dd, babjiSrc };
                    return (
                      <tr
                        key={t.id}
                        className={`border-b border-border hover:bg-muted/20 transition-colors ${
                          !hasDrawdownData
                            ? "bg-amber-500/5 dark:bg-amber-900/10 border-l-4 border-l-amber-500/50"
                            : ""
                        }`}
                      >
                        {visibleTableColumns.map((col) =>
                          renderTradeTableCell(t, col.key, ctx)
                        )}
                      </tr>
                    );
                  })}
            </tbody>
          </table>
        </div>

        {!loading && totalPages > 1 && (
          <div className="flex flex-col gap-3 border-t border-border px-2 py-2 sm:px-3 sm:py-2.5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <p className="text-sm text-muted-foreground">
              Page {page + 1} of {totalPages}
            </p>
            <div className="grid grid-cols-2 gap-2 sm:flex">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-md px-3 py-1.5 text-sm font-medium bg-muted text-muted-foreground hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="rounded-md px-3 py-1.5 text-sm font-medium bg-muted text-muted-foreground hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
