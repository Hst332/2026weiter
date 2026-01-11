import numpy as np

def model_score(df):
    """
    Final probabilistic score (prob_up)
    - centered around 0.50
    - no hard clipping to 0/1
    - compatible with backtests
    """

    close = df["Close"]

    # returns
    r_5  = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6]
    r_20 = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21]

    # weighted momentum (soft)
    raw = 0.6 * r_5 + 0.4 * r_20

    # squash into probability (logistic)
    prob = 1 / (1 + np.exp(-12 * raw))

    # safety clamp (never 0 or 1)
    prob = float(np.clip(prob, 0.40, 0.70))

    return prob
