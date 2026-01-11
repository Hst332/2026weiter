def interpret_regime(regime):
    texts = {
        "Reflation": "Wachstum und Inflation steigen gemeinsam.",
        "Stagflation": "Hohe Inflation bei schwachem Wachstum.",
        "Recession": "Nachfrageeinbruch dominiert.",
        "Risk-Off": "Kapitalflucht in sichere Assets.",
        "Transition": "Uneindeutige Übergangsphase."
    }
    return texts.get(regime, "")

def regime_confidence(gas, metals):
    copper = next(m for m in metals if m["commodity"] == "Copper")
    spread = abs(gas["bull"] - copper["bull"])
    if spread > 20:
        return "hoch"
    if spread > 10:
        return "mittel"
    return "niedrig"

def macro_regime_output(regime, gas, metals):
    return {
        "macro_regime": regime,
        "confidence": regime_confidence(gas, metals),
        "interpretation": interpret_regime(regime)
    }
