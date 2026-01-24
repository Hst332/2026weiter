def forecast_asset(asset, ticker, macro_bias):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    if df.empty or len(df) < 30:
        raise ValueError(f"Not enough data for {asset}")

    close = round(df["Close"].iloc[-1].item(), 1)

    score = model_score(df)

    f_1_5 = forecast_trend(df, days=5)
    f_2_3 = forecast_trend(df, days=15)

    # ---- MINI BACKTEST LOG (HIER GEHÖRT ES HIN) ----
    print(
        f"{asset:<10} | SCORE={score:.3f} | "
        f"1-5D={f_1_5:+.3f} | 2-3W={f_2_3:+.3f}"
    )

    decision = decide(
        asset=asset,
        score=score,
        signal_1_5d=f_1_5,
        signal_2_3w=f_2_3,
        macro_bias=macro_bias
    )

    return {
        "asset": asset,
        "close": close,
        "score": score,
        "signal": decision["final"],
        "f_1_5": f_1_5,
        "f_2_3": f_2_3,
        "gpt_1_5d": decision["gpt_1_5d"],
        "gpt_2_3w": decision["gpt_2_3w"],
        "final": decision["final"],
    }
