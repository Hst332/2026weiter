# forecast_gas.py

from metals_bundle import load_gas
from forecast_utils import model_score, forecast_trend, trade_signal
from datetime import datetime

def gas_result():
    df = load_gas()

    close = float(df["Close"].iloc[-1])
    score = model_score(df)

    return {
        "asset": "NATURAL GAS",
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "close": f"{close:.2f} USD/MMBtu",
        "model_score": f"{score:.2%}",
        "signal": trade_signal(score),
        "forecast_1_5d": forecast_trend(df, 5),
        "forecast_2_3w": forecast_trend(df, 21),
        "strategy": "Lev ≤ 10 | SL −20 %"
    }
