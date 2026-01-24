import yfinance as yf
import numpy as np
import pandas as pd

from model_core import model_score

print("[START] Silver backtest")

df = yf.download("SI=F", period="10y", interval="1d", progress=False)
df = df.dropna()

scores = []
future_returns = []

HOLD_DAYS = 10   # Silver etwas länger halten

for i in range(30, len(df) - HOLD_DAYS):
    window = df.iloc[:i]
    score = model_score(window)

    future_ret = (
        df["Close"].iloc[i + HOLD_DAYS]
        - df["Close"].iloc[i]
    ) / df["Close"].iloc[i]

    scores.append(score)
    future_returns.append(future_ret)

scores = np.array(scores)
future_returns = np.array(future_returns)
