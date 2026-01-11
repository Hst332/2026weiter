# forecast_silver.py

from metals_bundle import load_silver
from forecast_utils import model_score, forecast_trend, trade_signal
from datetime import datetime

def silver_result():
    df = load_silver()

    close = float(df["Close"].iloc[-1])
    score = model_score(df)

    return {
        "asset": "SILVER",
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "close": f"{close:.2f} USD/oz",
        "model_score": f"{score:.2%}",
        "signal": trade_signal(score),
        "forecast_1_5d": forecast_trend(df, 5),
        "forecast_2_3w": forecast_trend(df, 21),
        "strategy": "Long only | Lev ≤ 15 | SL −20 %"
    }
