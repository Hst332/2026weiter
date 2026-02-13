from __future__ import annotations

import os
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf


# Persistente Logs (werden im Repo committed, wenn dein Workflow das macht)
TRADE_LOG_FILE = os.path.join(os.path.dirname(__file__), "trade_log.csv")


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_yfinance_df(df: pd.DataFrame) -> pd.DataFrame:
    # yfinance + pandas 3 -> manchmal MultiIndex-Spalten
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def _download_daily(ticker: str, period: str = "2y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d", progress=False)
    df = _normalize_yfinance_df(df)
    # Index auf Date-only bringen (Tradingdays)
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.tz_localize(None).normalize()
    return df


def _to_date(s: str):
    # erwartet "YYYY-MM-DD" oder "YYYY-MM-DD HH:MM"
    try:
        return pd.to_datetime(s).normalize()
    except Exception:
        return None


def record_signals(results: list[dict], asset_to_ticker: dict[str, str]) -> None:
    """
    Speichert die heutigen FINAL-Signale (LONG/SHORT/NO_TRADE/NO_TRADE(DATA)).
    Nur wenn DATA_OK=True und FINAL in {LONG,SHORT} wird als "Trade-Signal" geloggt.
    """
    rows = []
    now_utc = _utc_now_str()

    for r in results:
        asset = r.get("asset", "NA")
        ticker = asset_to_ticker.get(asset)
        if not ticker:
            continue

        data_ok = bool(r.get("data_ok", False))
        final = str(r.get("final", "NO_TRADE"))

        # Wir loggen nur handelbare Signale (LONG/SHORT) bei DATA_OK
        if not data_ok:
            continue
        if final not in ("LONG", "SHORT"):
            continue

        signal_date_str = str(r.get("last_bar_utc_display") or r.get("last_bar_utc") or "")
        signal_date = _to_date(signal_date_str)
        if signal_date is None:
            continue

        close = r.get("close")
        try:
            close = float(close)
        except Exception:
            close = None

        rows.append({
            "time_utc": now_utc,
            "asset": asset,
            "ticker": ticker,
            "signal_date": signal_date.strftime("%Y-%m-%d"),
            "direction": final,          # LONG / SHORT
            "entry_close": close,        # Close am Signal-Tag (aus deinem Output)
            "horizon_days": 5,           # 1-5D Horizont -> 5 Tradingdays
            "evaluated": 0,
            "exit_date": "",
            "exit_close": "",
            "return": "",
            "correct": "",
        })

    if not rows:
        return

    df_new = pd.DataFrame(rows)

    if os.path.exists(TRADE_LOG_FILE):
        df_old = pd.read_csv(TRADE_LOG_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    # Duplikate verhindern (gleicher Asset + signal_date + direction)
    df_all = df_all.drop_duplicates(subset=["asset", "signal_date", "direction"], keep="first")

    df_all.to_csv(TRADE_LOG_FILE, index=False)


def evaluate_open_trades(asset_to_ticker: dict[str, str], horizon_days: int = 5) -> dict:
    """
    Bewertet alle offenen Signale aus trade_log.csv:
    - LONG richtig, wenn Close(t+h) > Close(t)
    - SHORT richtig, wenn Close(t+h) < Close(t)
    Speichert Ergebnis zurück in trade_log.csv und liefert Stats.
    """
    if not os.path.exists(TRADE_LOG_FILE):
        return {"overall": {"trades": 0, "correct": 0, "wrong": 0, "accuracy": None}, "by_asset": {}}

    log = pd.read_csv(TRADE_LOG_FILE)

    if log.empty:
        return {"overall": {"trades": 0, "correct": 0, "wrong": 0, "accuracy": None}, "by_asset": {}}

    # nur passende horizon_days auswerten
    log["horizon_days"] = log["horizon_days"].fillna(horizon_days).astype(int)

    open_mask = (log["evaluated"].fillna(0).astype(int) == 0) & (log["horizon_days"] == horizon_days)
    open_rows = log[open_mask].copy()

    if open_rows.empty:
        return _compute_stats(log)

    # pro ticker einmal laden
    tickers = sorted(set(open_rows["ticker"].dropna().astype(str).tolist()))
    market_data = {}
    for t in tickers:
        try:
            market_data[t] = _download_daily(t, period="2y")
        except Exception:
            market_data[t] = pd.DataFrame()

    # auswerten
    for idx, row in open_rows.iterrows():
        ticker = str(row["ticker"])
        asset = row["asset"]
        direction = str(row["direction"])
        sig_date = _to_date(str(row["signal_date"]))
        h = int(row["horizon_days"])

        df = market_data.get(ticker)
        if df is None or df.empty or "Close" not in df.columns or sig_date is None:
            continue

        # signal_date muss im Index sein (Tradingday)
        if sig_date not in df.index:
            # falls Wochenende/Feiertag: nächster Tradingday nach signal_date
            later = df.index[df.index >= sig_date]
            if len(later) == 0:
                continue
            sig_date = later[0]

        # Entry Close
        entry_close = df.loc[sig_date, "Close"]
        try:
            entry_close = float(entry_close)
        except Exception:
            continue

        # Exit = h Tradingdays später
        pos = df.index.get_loc(sig_date)
        exit_pos = pos + h
        if exit_pos >= len(df.index):
            continue  # noch nicht genug Zukunftsdaten -> später auswerten

        exit_date = df.index[exit_pos]
        exit_close = float(df.loc[exit_date, "Close"])

        ret = (exit_close / entry_close) - 1.0
        correct = 1 if ((direction == "LONG" and ret > 0) or (direction == "SHORT" and ret < 0)) else 0

        # in original log schreiben (über Index matching)
        # Wir matchen über asset+signal_date+direction
        m = (
            (log["asset"] == asset) &
            (log["signal_date"].astype(str) == row["signal_date"].astype(str)) &
            (log["direction"] == direction) &
            (log["horizon_days"] == h)
        )
        if m.any():
            log.loc[m, "evaluated"] = 1
            log.loc[m, "exit_date"] = pd.to_datetime(exit_date).strftime("%Y-%m-%d")
            log.loc[m, "exit_close"] = round(exit_close, 6)
            log.loc[m, "return"] = round(ret, 6)
            log.loc[m, "correct"] = int(correct)

    log.to_csv(TRADE_LOG_FILE, index=False)
    return _compute_stats(log)


def _compute_stats(log: pd.DataFrame) -> dict:
    done = log[log["evaluated"].fillna(0).astype(int) == 1].copy()
    done["correct"] = done["correct"].fillna("").astype(str)

    def _acc(df):
        trades = len(df)
        if trades == 0:
            return {"trades": 0, "correct": 0, "wrong": 0, "accuracy": None}
        c = (df["correct"] == "1").sum()
        w = (df["correct"] == "0").sum()
        acc = round(c / trades, 4)
        return {"trades": trades, "correct": int(c), "wrong": int(w), "accuracy": acc}

    overall = _acc(done)
    by_asset = {}
    for asset, g in done.groupby("asset"):
        by_asset[asset] = _acc(g)

    return {"overall": overall, "by_asset": by_asset}
