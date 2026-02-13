from forecast_assets import run_all
from forecast_writer import write_daily_summary


from signal_guard import (
    audit_and_format_signal,
    print_audit_header,
    print_audit_row,
    append_audit_jsonl
)

def main():
    print("MAIN STARTED")
    results = run_all()
    print("RESULTS:", results)
    write_daily_summary(results)
    print("FILE WRITTEN")


if __name__ == "__main__":
    main()
