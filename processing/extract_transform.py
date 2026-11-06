import re


def extract(row: str) -> str | None:
    pattern = re.compile(r"(?P<month>\w{3})\s(?P<day>\d{1,2})\s(?P<time>\d{2}:\d{2}:\d{2})\s.+:\s(?P<message>\w+)")
    match = re.search(pattern, row)
    if match:
        return match.group(4)
    return None
