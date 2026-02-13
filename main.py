"""
main_with_guard_output.py

- Erweiterter Tabellen-Output inkl. Data-Guard (DATA_OK, LAST_BAR, AGE_s, NAN_LAST, STALE)
- Erzwingt: FINAL = NO_TRADE(DATA) wenn Daten unplausibel / alt / NaN / zu kurz
- Für manuelles Intraday-Trading gedacht.

Voraussetzung:
- pandas installiert
- Du hast je Asset einen DataFrame df mit DateTimeIndex
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import pandas as pd


# ==========================================================
# GUARD (wie signal_guard.py, hier vollständig eingebettet)
# ==========================================================

@dataclass
class GuardResult:
    asset: str
    data_ok: bool
    last_bar_str: str
    age_s: int
    rows: int
    nan_last: int
    stale: int
    reason: str


def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def guard_intraday_data(
    asset: str,
    df: pd.DataFrame,
    *,
    timeframe_seconds: int = 60,          # 1m default
    max_stale_multiplier: int = 2,        # stale wenn > timeframe * multiplier
    min_rows: int = 200,
    required_cols: tuple = ("Open", "High", "Low", "Close", "Volume"),
    critical_last_cols: tuple = ("Close", "Volume"),
    assume_index_is_utc: bool = True
) -> GuardResult:
    reasons = []
    data_ok = True

    if df is None or len(df) == 0:
        data_ok = False
        reasons.append("EMPTY_DF")
        return GuardResult(asset, False, "NA", 10**9, 0, 1, 1, ";".join(reasons))

    rows = len(df)

    # Columns present?
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        data_ok = False
        reasons.append("MISSING_COLS:" + ",".join(missing))

    # Minimum history
    if rows < min_rows:
        data_ok = False
        reasons.append("HISTORY_SHORT")

    # Last timestamp
    try:
        last_bar_dt = df.index[-1]
        if isinstance(last_bar_dt, pd.Timestamp):
            last_bar_dt = last_bar_dt.to_pydatetime()
    except Exception:
        data_ok = False
        reasons.append("BAD_INDEX")
        return GuardResult(asset, False, "NA", 10**9, rows, 1, 1, ";".join(reasons))

    # Stale check
    now_utc = datetime.now(timezone.utc)
    if last_bar_dt.tzinfo is None:
        if assume_index_is_utc:
            last_bar_dt = last_bar_dt.replace(tzinfo=timezone.utc)
        else:
            last_bar_dt = last_bar_dt.replace(tzinfo=timezone.utc)

    age_s = _safe_int((now_utc - last_bar_dt).total_seconds(), 10**9)
    max_stale_seconds = timeframe_seconds * max_stale_multiplier
    stale = 1 if age_s > max_stale_seconds else 0
    if stale:
        data_ok = False
        reasons.append("STALE_DATA")

    last_bar_str = last_bar_dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    # NaN last row check
    nan_last = 0
    for c in critical_last_cols:
        if c in df.columns and pd.isna(df[c].iloc[-1]):
            nan_last = 1
            break
    if nan_last:
        data_ok = False
        reasons.append("NAN_LAST_ROW")

    reason = "OK" if data_ok else ";".join(reasons)
    return GuardResult(asset, data_ok, last_bar_str, age_s, rows, nan_last, stale, reason)


# ==========================================================
# DEIN RESULT-ROW (dein bestehendes Format + Guard-Spalten)
# ==========================================================

@dataclass
class Row:
    asset: str
    close: float
    score: float
    signal: str        # z.B. "TRADE" / "NO_TRADE" (deine Logik)
    f_1_5d: float
    f_2_3w: float
    gpt_1_5d: str
    gpt_2_3w: str
    final: str         # z.B. "LONG"/"SHORT"/"NO_TRADE"
    zusatz: str


def format_table(rows, guard_map, runtime_utc_str: str):
    # Header
    print(f"Run time (UTC): {runtime_utc_str}")
    print("=" * 140)
    print(
        "ASSET         CLOSE     SCORE   SIGNAL       1-5D      2-3W      GPT 1-5D   GPT 2-3W   "
        "FINAL           DATA_OK  LAST_BAR            AGE_s  NAN_LAST  STALE  ZUSATZINFO"
    )
    print("-" * 140)

    for r in rows:
        g = guard_map.get(r.asset)

        # Guard erzwingt FINAL:
        final_for_trade = r.final
        if g is None or not g.data_ok:
            final_for_trade = "NO_TRADE(DATA)"

        # Print row
        close_str = f"{r.close:.1f}" if r.close is not None else "NA"
        print(
            f"{r.asset:<12}  "
            f"{close_str:>7}  "
            f"{r.score:>7.3f}  "
            f"{r.signal:<9}  "
            f"{r.f_1_5d:>8.4f}  "
            f"{r.f_2_3w:>8.4f}  "
            f"{r.gpt_1_5d:<9}  "
            f"{r.gpt_2_3w:<9}  "
            f"{final_for_trade:<14}  "
            f"{str(g.data_ok) if g else 'False':<6}  "
            f"{g.last_bar_str if g else 'NA':<19}  "
            f"{g.age_s if g else 10**9:>5}  "
            f"{g.nan_last if g else 1:>8}  "
            f"{g.stale if g else 1:>5}  "
            f"{r.zusatz}"
        )

        # Wenn Guard fail: Grund direkt darunter (damit du es sofort siehst)
        if g is None or not g.data_ok:
            reason = g.reason if g else "NO_GUARD_RESULT"
            print(f"{'':<12}  >>> BLOCKED: {reason}")

    print("=" * 140)


# ==========================================================
# HIER: DEINE PIPELINE EINHÄNGEN
# ==========================================================

def main():
    runtime_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------
    # 1) Hier stellst du deine DataFrames bereit (aus deinem Code)
    #    WICHTIG: df.index muss DateTime sein!
    # ------------------------------------------------------
    #
    # Beispiel-Platzhalter: Ersetze durch deinen echten Code:
    #
    # df_gold = get_data("GOLD")
    # df_silver = get_data("SILVER")
    # df_gas = get_data("NATURAL GAS")
    # df_copper = get_data("COPPER")
    #
    # Für Demo erzeugen wir minimal sinnvolle Fake-DFs:
    import numpy as np
    now = datetime.now(timezone.utc)
    idx = pd.date_range(end=now, periods=300, freq="1min")

    def fake_df():
        return pd.DataFrame(
            {
                "Open": np.random.random(len(idx)),
                "High": np.random.random(len(idx)),
                "Low": np.random.random(len(idx)),
                "Close": np.random.random(len(idx)) * 100 + 1,
                "Volume": np.random.randint(100, 1000, len(idx)),
            },
            index=idx,
        )

    df_gold = fake_df()
    df_silver = fake_df()
    df_gas = fake_df()
    df_copper = fake_df()

    dataframes = {
        "GOLD": df_gold,
        "SILVER": df_silver,
        "NATURAL GAS": df_gas,
        "COPPER": df_copper,
    }

    # ------------------------------------------------------
    # 2) Guard für alle Assets berechnen
    #    timeframe_seconds MUSS zu deinem Intraday-Chart passen!
    #    (1m=60, 5m=300, 15m=900, ...)
    # ------------------------------------------------------
    timeframe_seconds = 60
    guard_map = {}
    for asset, df in dataframes.items():
        guard_map[asset] = guard_intraday_data(
            asset=asset,
            df=df,
            timeframe_seconds=timeframe_seconds,
            max_stale_multiplier=2,
            min_rows=200,
            required_cols=("Open", "High", "Low", "Close", "Volume"),
            critical_last_cols=("Close", "Volume"),
            assume_index_is_utc=True,
        )

    # ------------------------------------------------------
    # 3) Hier kommen deine echten Modell-Ergebnisse rein
    #    (SCORE, SIGNAL, Forecasts, GPT-Labels, FINAL, Zusatzinfo)
    #    Ich trage Demo-Werte ein – du ersetzt sie 1:1 durch deine Werte.
    # ------------------------------------------------------
    rows = [
        Row("GOLD", float(df_gold["Close"].iloc[-1]), 0.599, "TRADE", 0.0005, -0.0052, "Neutral", "Neutral", "LONG", "Gold-Regel aktiv"),
        Row("SILVER", float(df_silver["Close"].iloc[-1]), 0.464, "NO_TRADE", -0.0518, -0.3239, "Neutral", "Neutral", "NO_TRADE", "Score unter Silver-Entry"),
        Row("NATURAL GAS", float(df_gas["Close"].iloc[-1]), 0.494, "NO_TRADE", 0.0379, -0.5210, "Neutral", "Neutral", "NO_TRADE", "Gas Neutralzone"),
        Row("COPPER", float(df_copper["Close"].iloc[-1]), 0.459, "NO_TRADE", -0.0216, -0.0280, "Neutral", "Neutral", "NO_TRADE", "Score unter Copper-Entry"),
    ]

    # ------------------------------------------------------
    # 4) Ausgabe
    # ------------------------------------------------------
    format_table(rows, guard_map, runtime_utc)


if __name__ == "__main__":
    main()
