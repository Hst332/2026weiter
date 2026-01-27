from datetime import datetime, timezone
import json
from pathlib import Path

def write_forecasts(forecasts):
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    # Root-Verzeichnis
    root = Path(".")
    txt_file = root / "index_forecast.txt"

    forecasts_dir = root / "forecasts"
    daily = forecasts_dir / "daily"
    history = forecasts_dir / "history"

    daily.mkdir(parents=True, exist_ok=True)
    history.mkdir(parents=True, exist_ok=True)

    # Daily JSON
    with open(daily / f"{now.date().isoformat()}.json", "w") as f:
        json.dump(forecasts, f, indent=2)

    # History JSON
    history_file = history / "all_forecasts.json"
    history_data = []

    if history_file.exists():
        with open(history_file) as f:
            history_data = json.load(f)

    history_data.append({
        "timestamp": timestamp,
        "forecasts": forecasts
    })

    with open(history_file, "w") as f:
        json.dump(history_data, f, indent=2)

    # 🔥 EINZIGE TXT-DATEI (überschreiben!)
    with open(txt_file, "w") as f:
        f.write(f"Index Forecasts – {timestamp}\n")
        f.write("=" * 45 + "\n\n")

        for item in forecasts:
            f.write(
                f"{item['asset']}: "
                f"{item['signal']} "
                f"(Confidence: {item['confidence']:.2f}, "
                f"Regime: {item['regime']})\n"
            )
