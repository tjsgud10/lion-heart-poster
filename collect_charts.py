import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent / "data"
SOURCES = {"global": ("Global", None), "kr": ("South Korea", "Korea, Republic of"),
           "jp": ("Japan", "Japan")}


def collect(key, root=ROOT, fetch=urlopen, day=None):
    day = day or datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
    failures = 0
    for slug, (label, country) in SOURCES.items():
        params = {"method": "geo.gettoptracks" if country else "chart.gettoptracks",
                  "api_key": key, "format": "json", "limit": 50}
        if country:
            params["country"] = country
        try:
            with fetch("https://ws.audioscrobbler.com/2.0/?" + urlencode(params), timeout=25) as reply:
                payload = json.load(reply)
            raw = payload["tracks"]["track"]
            tracks = [{"title": row["name"], "artist": row["artist"]["name"]}
                      for row in raw if row["name"] and row["artist"]["name"]]
            if not tracks:
                raise ValueError("Empty chart")
        except (OSError, ValueError, TypeError, KeyError):
            failures += 1
            print(f"{label}: 수집 실패, 기존 자료 유지")
            continue

        chart = root / "charts" / f"{slug}.json"
        history = root / "history" / f"{slug}.csv"
        chart.parent.mkdir(parents=True, exist_ok=True)
        history.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        if history.exists():
            with history.open(encoding="utf-8", newline="") as file:
                rows = [row for row in csv.DictReader(file) if row["date"] != day]
        rows.extend(dict(date=day, rank=i, **track) for i, track in enumerate(tracks, 1))
        rows.sort(key=lambda row: (row["date"], int(row["rank"])))
        with history.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "rank", "title", "artist"])
            writer.writeheader()
            writer.writerows(rows)
        chart.write_text(json.dumps({"label": label, "tracks": tracks}, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    if failures == len(SOURCES):
        raise SystemExit("모든 차트 수집이 실패했습니다.")


if __name__ == "__main__":
    api_key = os.environ.get("LASTFM_API_KEY")
    if api_key:
        collect(api_key)
    else:
        print("LASTFM_API_KEY 미설정. 차트 수집을 건너뜁니다.")
