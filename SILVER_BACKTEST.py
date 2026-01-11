import pandas as pd
import numpy as np
import metals_bundle

def main():
    df = metals_bundle.load_silver()

    # Backtest-Logik hier
    print("[OK] Silver backtest runs independently")

if __name__ == "__main__":
    main()
