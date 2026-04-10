from __future__ import annotations

import json
import os
import unicodedata
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request

APP_TITLE = "ICM Meteo - Prognoza"


def _strip_extended_prefix(path: str) -> str:
    # Jinja can fail to resolve templates when Windows extended paths (\\?\\) are used.
    if path.startswith("\\\\?\\"):
        return path[4:]
    return path


BASE_DIR = _strip_extended_prefix(os.path.dirname(os.path.abspath(__file__)))
CITIES_PATH = os.path.join(BASE_DIR, "data", "cities.json")

ICM_METEOGRAM_URL = "https://www.meteo.pl/um/metco/mgram_pict.php"

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def load_cities():
    if not os.path.exists(CITIES_PATH):
        return []
    with open(CITIES_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data


def latest_fdate(now: datetime) -> str:
    # Prosta heurystyka cykli 00/06/12/18 z uwzglednieniem opoznienia publikacji
    hour = now.hour
    if hour < 10:
        dt = (now - timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    elif hour < 12:
        dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif hour < 19:
        dt = now.replace(hour=6, minute=0, second=0, microsecond=0)
    else:
        dt = now.replace(hour=12, minute=0, second=0, microsecond=0)
    return dt.strftime("%Y%m%d%H")


def build_meteogram_url(row: int, col: int, fdate: str) -> str:
    return f"{ICM_METEOGRAM_URL}?ntype=0u&fdate={fdate}&row={row}&col={col}&lang=pl"


CITIES = load_cities()


@app.get("/")
def index():
    return render_template(
        "index.html",
        app_title=APP_TITLE,
        cities=CITIES,
    )


@app.get("/api/meteogram")
def api_meteogram():
    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Brakuje parametru name."}), 400

    nq = _normalize(name)
    city = next((c for c in CITIES if _normalize(c.get("name", "")) == nq), None)
    if not city:
        return jsonify({"error": "Nie znaleziono miasta."}), 404

    fdate = latest_fdate(datetime.now())
    url = build_meteogram_url(city["row"], city["col"], fdate)

    return jsonify(
        {
            "name": city["name"],
            "row": city["row"],
            "col": city["col"],
            "fdate": fdate,
            "url": url,
        }
    )


@app.get("/health")
def health():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
