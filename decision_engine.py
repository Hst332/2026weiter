def trade_signal(asset, prob_up):
    asset = asset.upper()

    # GOLD
    if asset == "GOLD":
        if prob_up >= 0.55:
            return "LONG_FULL"
        elif prob_up >= 0.53:
            return "LONG_HALF"
        else:
            return "NO_TRADE"

    # SILVER
    if asset == "SILVER":
        return "LONG" if prob_up >= 0.96 else "NO_TRADE"

    # COPPER
    if asset == "COPPER":
        return "LONG" if prob_up >= 0.56 else "NO_TRADE"

    # NATURAL GAS
    if asset == "NATURAL GAS":
        if prob_up >= 0.56:
            return "LONG"
        elif prob_up <= 0.44:
            return "SHORT"
        else:
            return "NO_TRADE"

    return "NO_TRADE"
