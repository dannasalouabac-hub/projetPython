from datetime import datetime
import re

from processing import extract_transform, geolocation


def process_rows(
    rows: list[str],
) -> list[tuple[str | None, str, str, str, str | None, str | None, str | None, str]]:
    invalid_user = 0
    failed_password = 0
    successful_connections = 0
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

        if result not in ("Failed", "Invalid", "Accepted"):
            continue

        actor = "Bot" if bot else "Human"
        username = None
        if result == "Accepted":
            username_match = re.search(
                r"\bAccepted\s+\S+\s+for\s+(?:invalid user\s+)?(?P<username>\S+)\s+from\b",
                row,
            )
            if not username_match:
                continue
            username = username_match.group("username")
            city = None
            country = None
            successful_connections += 1
            print(f"Successful connection | User: {username} | IP: {ip}")
        else:
            location = geolocation.geo_location(ip)
            city = location["city"]
            country = location["country"]

        if result == "Failed":
            failed_password += 1
            print(f"Failed password | IP: {ip} | {actor}")
        elif result == "Invalid":
            invalid_user += 1
            print(f"Invalid user | IP: {ip} | {actor}")

        if city is not None and country is not None:
            print(f"Location: {city}, {country}")
        events.append(
            (
                time_match.group() if time_match else None,
                result,
                ip,
                actor,
                city,
                country,
                username,
                row.strip(),
            )
        )

    print(f"\nFailed password count: {failed_password}")
    print(f"Invalid user count: {invalid_user}")
    print(f"Successful connection count: {successful_connections}")
    return events
