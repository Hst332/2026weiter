import pandas as pd


def forecast_trend(df, days=5) -> float:
    close = df["Close"]

    # Robust gegen Series ODER DataFrame
    if isinstance(close, pd.DataFrame):
        last = float(close.iloc[-1, 0])
        past = float(close.iloc[-days, 0])
    else:
        last = float(close.iloc[-1])
        past = float(close.iloc[-days])

    return round((last - past) / past, 4)
