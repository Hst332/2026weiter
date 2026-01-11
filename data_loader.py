import yfinance as yf
import pandas as pd


def load_asset(ticker: str, period="2y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, progress=False)
    if df.empty:
        raise RuntimeError(f"No data for {ticker}")
    df = df.dropna()
    return df
