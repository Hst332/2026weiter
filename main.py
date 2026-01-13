from forecast_assets import run_all
from forecast_writer import write_daily_summary

def main():
    print("MAIN STARTED")
    results = run_all()
    print("RESULTS:", results)
    write_daily_summary(results)
    print("FILE WRITTEN")


if __name__ == "__main__":
    main()
