import metals_bundle
from forecast_utils import model_score, forecast_trend, trade_signal

def copper_result():
    df = metals_bundle.load_copper()
    
    close = df["Close"]
    if hasattr(close, "columns"):
        close = close.iloc[:, 0]
    close = float(close.iloc[-1])

    score = model_score(df)

    return {
        "asset": "COPPER",
        "date": df.index[-1].strftime("%Y-%m-%d"),
        "close": f"{close:.2f} USD/kg",
        "model_score": f"{score:.2%}",
        "signal": trade_signal(score),
        "forecast_1_5d": forecast_trend(df, 5),
        "forecast_2_3w": forecast_trend(df, 21),
        "strategy_lines": [
            "Industrial metal | China driven",
            "Cycle & infrastructure sensitive",
            "Phase-2 momentum model",
        ],
    }
