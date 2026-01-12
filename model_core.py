import numpy as np




def model_score(df) -> float:
    last = float(df["Close"].iloc[-1])
    past = float(df["Close"].iloc[-21])
    r = (last - past) / past


    raw = 0.5 + np.clip(r * 3.0, -0.2, 0.2)
    return round(float(np.clip(raw, 0.30, 0.70)), 3)
