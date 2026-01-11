def decide(asset, score):
    if asset == "GOLD":
        if score >= 0.55:
            return "LONG_FULL", "Gold: score ≥ 0.55 → full long"
        elif score >= 0.53:
            return "LONG_HALF", "Gold: score 0.53–0.55 → half long"
        else:
            return "NO_TRADE", "Gold: score < 0.53"

    if asset == "SILVER":
        if score >= 0.96:
            return "LONG", "Silver: score ≥ 0.96"
        else:
            return "NO_TRADE", "Silver below threshold"

    if asset == "COPPER":
        if score >= 0.56:
            return "LONG", "Copper: score ≥ 0.56"
        else:
            return "NO_TRADE", "Copper below threshold"

    if asset == "NATURAL GAS":
        if score >= 0.56:
            return "LONG", "Gas: prob_up ≥ 0.56"
        elif score <= 0.44:
            return "SHORT", "Gas: prob_up ≤ 0.44"
        else:
            return "NO_TRADE", "Gas neutral zone"

    return "NO_TRADE", "Unknown asset"


def log_decision(asset, score):
    signal, reason = decide(asset, score)
    print(f"[DECISION] {asset:12} | score={score:.3f} → {signal:10} | {reason}")
