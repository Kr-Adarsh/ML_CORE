import os
import csv
import requests
from datetime import datetime, timezone

OWNER = os.environ["TRAFFIC_OWNER"]
REPO = os.environ["TRAFFIC_REPO"]
TOKEN = os.environ["TRAFFIC_TOKEN"]

BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/traffic"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
}

def fetch(endpoint):
    url = BASE + endpoint
    r = requests.get(url, headers=HEADERS)
    
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    r.raise_for_status()
    return r.json()

def main():
    now = datetime.now(timezone.utc).isoformat()

    clones = fetch("/clones")
    views = fetch("/views")

    os.makedirs("traffic", exist_ok=True)
    file_exists = os.path.exists("traffic/traffic_log.csv")

    with open("traffic/traffic_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["captured_at_utc", "type", "timestamp_utc", "count", "uniques"])

        for row in clones.get("clones", []):
            writer.writerow([now, "clone", row["timestamp"], row["count"], row["uniques"]])

        for row in views.get("views", []):
            writer.writerow([now, "view", row["timestamp"], row["count"], row["uniques"]])

if __name__ == "__main__":
    main()