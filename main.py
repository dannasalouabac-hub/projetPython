from pathlib import Path

from ingestion import read
from processing import analyze
from storage import database


def main():
    data_directory = Path(__file__).resolve().parent / "data"
    rows = read.ingest(str(data_directory))
    events = analyze.process_rows(rows)
    database.save_events(events)


if __name__ == "__main__":
    main()