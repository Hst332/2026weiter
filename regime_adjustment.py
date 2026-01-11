def adjust_metals_for_regime(metals, regime):
    for m in metals:
        if regime == "Recession" and m["commodity"] in ["Silver", "Copper"]:
            m["bull"] -= 5
            m["bear"] += 5
        if regime == "Stagflation" and m["commodity"] == "Gold":
            m["bull"] += 5
            m["bear"] -= 5
    return metals
