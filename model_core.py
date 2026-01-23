import numpy as np
import pandas as pd

def compute_score(prices) -> float:
    """
    SCORE V2 – fully robust, production safe
    """

    # ---------- INPUT NORMALIZATION ----------
    if isinstance(prices, pd.DataFrame):
        # Case: MultiIndex columns (e.g. ('Close','GOLD'))
        if isinstance(prices.columns, pd.MultiIndex):
            close_cols = [c for c in prices.columns if c[0].lower() == "close"]
            if not close_cols:
                return 0.50
            p = prices[close_cols[0]].values

        # Case: normal DataFrame
        elif "Close" in prices.columns:
            p = prices["Close"].values

        else:
            p = prices.iloc[:, -1].values

    elif isinstance(prices, pd.Series):
        p = prices.values

    else:
        p = np.asarray(prices)

    # ---------- FORCE 1D FLOAT ARRAY ----------
    p = np.asarray(p, dtype=float).reshape(-1)

    # ---------- SAFETY ----------
    if len(p) < 30 or np.any(~np.isfinite(p)):
        return 0.50

    # ---------- RETURNS ----------
    r_20 = (p[-1] - p[-21]) / p[-21]
    r_5  = (p[-1] - p[-6])  / p[-6]

    # ---------- VOLATILITY ----------
    rets = np.diff(np.log(p[-21:]))

    vol = np.std(rets)
    if not np.isfinite(vol) or vol < 1e-6:
        return 0.50

    # ---------- NORMALIZED MOMENTUM ----------
    m20 = r_20 / (vol * np.sqrt(20))
    m5  = r_5  / (vol * np.sqrt(5))

    core = (
        0.65 * np.tanh(m20 * 0.8) +
        0.35 * np.tanh(m5  * 1.2)
    )

    score = 0.5 + core * 0.25
    return float(np.round(score, 3))


# backward compatibility
model_score = compute_score
