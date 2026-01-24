import yfinance as yf

from model_core import model_score
from forecast_utils import forecast_trend
from decision_engine import decide


# --------------------------------------------------
# ASSET DEFINITIONS
# --------------------------------------------------

ASSETS = [
    ("GOLD", "GC=F", "STRONG_SUPPORT"),
    ("SILVER", "SI=F", "NO_SUPPORT"),
    ("NATURAL GAS", "NG=F", "STRONG_SUPPORT"),
    ("COPPER", "HG=F", "STRONG_SUPPORT"),
]


# --------------------------------------------------
# SINGLE ASSET FORECAST
# --------------------------------------------------

def forecast_asset(asset, ticker, macro_bias):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    if df.empty or len(df) < 30:
        raise ValueError(f"Not enough data for {asset}")

    close = round(df["Close"].iloc[-1].item(), 1)

    score = model_score(df)

    f_1_5 = forecast_trend(df, days=5)
    f_2_3 = forecast_trend(df, days=15)

    # ---- MINI BACKTEST LOG ----
    print(
        f"{asset:<10} | SCORE={score:.3f} | "
        f"1-5D={f_1_5:+.3f} | 2-3W={f_2_3:+.3f}"
    )

    decision = decide(
        asset=asset,
        score=score,
        signal_1_5d=f_1_5,
        signal_2_3w=f_2_3,
        macro_bias=macro_bias
    )

    return {
    "asset": asset,
    "close": close,
    "score": score,
    "signal": decision["rule_signal"],   # nur Regelstatus
    "f_1_5": f_1_5,
    "f_2_3": f_2_3,
    "gpt_1_5d": decision["gpt_1_5d"],
    "gpt_2_3w": decision["gpt_2_3w"],
    "final": decision["action"],         # echte Handlung
    "zusatzinfo": decision["zusatzinfo"]
}



# --------------------------------------------------
# RUN ALL ASSETS  ← MUSS AUF MODULEBENE SEIN
# --------------------------------------------------

def run_all():
    results = []

    for asset, ticker, macro_bias in ASSETS:
        results.append(
            forecast_asset(asset, ticker, macro_bias)
        )

    return results
