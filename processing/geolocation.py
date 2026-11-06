import requests as http


def geo_location(ip):
    try:
        response = http.get(
            "https://ipinfo.io/" + ip + "/json?token=c32cbc8d6525ac",
            timeout=10,
        )
    except http.RequestException as error:
        print(
            f"Geolocation request failed for {ip} "
            f"({type(error).__name__}); using Unknown."
        )
        return {"country": "Unknown", "city": "Unknown"}

    if response.status_code == 200:
        result = response.json()
        return {
            "country": result.get("country", "Unknown"),
            "city": result.get("city", "Unknown"),
        }
    print("Geolocation request failed:", response.status_code)
    return {"country": "Unknown", "city": "Unknown"}


