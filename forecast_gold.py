from metals_bundle import load_gold
from forecast_utils import model_score, forecast_trend, trade_signal
from datetime import datetime




def gold_result():
    df = load_gold()
    
    
    close = df["Close"].iloc[-1].item()
    score = model_score(df)


    return {
        "asset": "GOLD",
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "close": f"{close:.2f} USD/oz",
        "model_score": f"{score:.2%}",
        "signal": trade_signal(score),
        "forecast_1_5d": forecast_trend(df, 5),
        "forecast_2_3w": forecast_trend(df, 15),
        }
