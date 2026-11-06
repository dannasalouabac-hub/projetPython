from datetime import datetime
import re
from pathlib import Path

from ingestion import read
from processing import extract_transform,geolocation
from storage import database


def main():
    data_directory = Path(__file__).resolve().parent / "data"
    rows = read.ingest(str(data_directory))
    invalid_user = 0
    failed_password = 0
    previous_ip = None
    previous_time = None
    events = []

    for row in rows:
        result = extract_transform.extract(row)
        match = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", row)
        ip = match.group() if match else "not found"
        time_match = re.search(r"\b[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b", row)
        event_time = None
        if time_match:
            event_time = datetime.strptime(time_match.group(), "%b %d %H:%M:%S")

        bot = (
            ip != "not found"
            and ip == previous_ip
            and event_time is not None
            and previous_time is not None
            and 0 <= (event_time - previous_time).total_seconds() < 3
        )

        if result in ("Failed", "Invalid", "Accepted"):
            previous_ip = ip
            previous_time = event_time

        if result not in ("Failed", "Invalid"):
            continue

        actor = "Bot" if bot else "Human"
        location = geolocation.geo_location(ip)
        city = location["city"]
        country = location["country"]

        if result == "Failed":
            failed_password += 1
            print(f"Failed password | IP: {ip} | {actor}")
        elif result == "Invalid":
            invalid_user += 1
            print(f"Invalid user | IP: {ip} | {actor}")

        print(f"Location: {city}, {country}")
        events.append(
            (
                time_match.group() if time_match else None,
                result,
                ip,
                actor,
                city,
                country,
                row.strip(),
            )
        )

    print(f"\nFailed password count: {failed_password}")
    print(f"Invalid user count: {invalid_user}")
    database.save_events(events)


if __name__ == "__main__":
    main()