def decide(asset, score, signal_1_5d, signal_2_3w, macro_bias):

    # Text-Einordnung (nur Info)
    gpt_1_5d = "Bullish" if signal_1_5d == "++" else "Bearish" if signal_1_5d == "--" else "Neutral"
    gpt_2_3w = "Bullish" if signal_2_3w == "++" else "Bearish" if signal_2_3w == "--" else "Neutral"

    SIGNAL = "NO_TRADE"
    FINAL = "NO_TRADE"
    ZUSATZINFO = ""

    # -----------------------------
    # GOLD
    # -----------------------------
    if asset == "GOLD":
        if score >= 0.53:
            SIGNAL = "TRADE"
            FINAL = "LONG"
            ZUSATZINFO = "Gold-Regel aktiv"
        else:
            ZUSATZINFO = "Score unter Gold-Entry"

    # -----------------------------
    # SILVER
    # -----------------------------
    elif asset == "SILVER":
        if score >= 0.69:
            SIGNAL = "TRADE"
            FINAL = "LONG"
            ZUSATZINFO = "Silver-Regel aktiv"
        else:
            ZUSATZINFO = "Score unter Silver-Entry"

    # -----------------------------
    # COPPER
    # -----------------------------
    elif asset == "COPPER":
        if score >= 0.56:
            SIGNAL = "TRADE"
            FINAL = "LONG"
            ZUSATZINFO = "Copper-Regel aktiv"
        else:
            ZUSATZINFO = "Score unter Copper-Entry"

    # -----------------------------
    # NATURAL GAS
    # -----------------------------
    elif asset == "NATURAL GAS":
        if score >= 0.56:
            SIGNAL = "TRADE"
            FINAL = "LONG"
            ZUSATZINFO = "Gas LONG-Regel"
        elif score <= 0.44:
            SIGNAL = "TRADE"
            FINAL = "SHORT"
            ZUSATZINFO = "Gas SHORT-Regel"
        else:
            ZUSATZINFO = "Gas Neutralzone"

    return {
    "rule_signal": SIGNAL,     # TRADE / NO_TRADE
    "action": FINAL,           # LONG / SHORT / NO_TRADE
    "gpt_1_5d": gpt_1_5d,
    "gpt_2_3w": gpt_2_3w,
    "zusatzinfo": ZUSATZINFO
}

