import numpy as np

def compute_score(prices: np.ndarray) -> float:
    """
    SCORE V2 – no saturation, volatility normalized
    prices: np.array of daily closes (newest last)
    """

    if len(prices) < 30:
        return 0.50

    p = prices.astype(float)

    # returns
    r_20 = (p[-1] - p[-21]) / p[-21]
    r_5  = (p[-1] - p[-6])  / p[-6]

    # volatility (log-returns)
    rets = np.diff(np.log(p[-21:]))
    vol  = np.std(rets) + 1e-6

    # normalized momentum
    m20 = r_20 / (vol * np.sqrt(20))
    m5  = r_5  / (vol * np.sqrt(5))

    # soft squash (NO HARD CAPS)
    core = (
        0.65 * np.tanh(m20 * 0.8) +
        0.35 * np.tanh(m5  * 1.2)
    )

    score = 0.5 + core * 0.25
    return round(float(score), 3)
    # backward compatibility
    model_score = compute_score
