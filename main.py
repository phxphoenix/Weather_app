import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk

import requests
from PIL import Image, ImageTk
from io import BytesIO

APP_TITLE = "ICM Meteo – Prognoza"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CITIES_PATH = os.path.join(BASE_DIR, "data", "cities.json")

ICM_METEOGRAM_URL = "https://www.meteo.pl/um/metco/mgram_pict.php"

COLOR_BG = "#dff1ff"
COLOR_PANEL = "#f4fbff"
COLOR_CARD = "#eef8ff"
COLOR_ACCENT = "#5aa7e8"
COLOR_TEXT = "#1a2a3a"


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def load_cities():
    base = getattr(sys, '_MEIPASS', BASE_DIR)
    cities_path = os.path.join(base, 'data', 'cities.json')
    if not os.path.exists(cities_path):
        return []
    # Handle potential UTF-8 BOM in JSON file
    with open(cities_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data


def latest_fdate(now: datetime) -> str:
    # Prosta heurystyka cykli 00/06/12/18 z uwzględnieniem opóźnienia publikacji
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
    return (
        f"{ICM_METEOGRAM_URL}?ntype=0u&fdate={fdate}&row={row}&col={col}&lang=pl"
    )


def fetch_meteogram(row: int, col: int) -> Image.Image:
    fdate = latest_fdate(datetime.now())
    url = build_meteogram_url(row, col, fdate)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content))


def split_image_by_days(img: Image.Image, days: int = 4):
    w, h = img.size
    segment_w = w // days
    parts = []
    for i in range(days):
        left = i * segment_w
        right = w if i == days - 1 else (i + 1) * segment_w
        parts.append(img.crop((left, 0, right, h)))
    return parts


def concat_images_horizontally(parts):
    if not parts:
        return None
    total_w = sum(p.size[0] for p in parts)
    max_h = max(p.size[1] for p in parts)
    out = Image.new("RGB", (total_w, max_h), (255, 255, 255))
    x = 0
    for p in parts:
        out.paste(p, (x, 0))
        x += p.size[0]
    return out


class MeteoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x720")
        self.configure(bg=COLOR_BG)

        self.cities = load_cities()
        self.filtered_cities = list(self.cities)

        self.search_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Wpisz miasto i wybierz z listy.")

        self._image_refs = []
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg=COLOR_BG)
        header.pack(fill="x", padx=20, pady=16)

        title = tk.Label(
            header,
            text="Prognoza ICM (meteo.pl)",
            font=("Segoe UI", 20, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
        )
        title.pack(anchor="w")

        search_bar = tk.Frame(self, bg=COLOR_PANEL, highlightbackground=COLOR_ACCENT, highlightthickness=1)
        search_bar.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(
            search_bar,
            text="Miasto",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_PANEL,
        ).pack(side="left", padx=(12, 8), pady=10)

        search_entry = tk.Entry(
            search_bar,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=30,
            relief="flat",
            bg="#ffffff",
        )
        search_entry.pack(side="left", padx=(0, 10), pady=10)

        search_btn = tk.Button(
            search_bar,
            text="Szukaj",
            command=self.on_search,
            bg=COLOR_ACCENT,
            fg="white",
            relief="flat",
            padx=16,
            pady=6,
        )
        search_btn.pack(side="left", padx=(0, 12), pady=10)

        self.city_combo = ttk.Combobox(
            search_bar,
            textvariable=self.city_var,
            state="readonly",
            values=[c["name"] for c in self.filtered_cities],
            width=30,
        )
        self.city_combo.pack(side="left", padx=(0, 12), pady=10)
        self.city_combo.bind("<<ComboboxSelected>>", self.on_city_selected)

        info = tk.Label(
            self,
            text="Dane: meteo.pl (ICM UW). Meteogram podzielony na dni dla czytelnej prezentacji.",
            font=("Segoe UI", 10),
            fg="#3a5166",
            bg=COLOR_BG,
        )
        info.pack(anchor="w", padx=20)

        self.cards_frame = tk.Frame(self, bg=COLOR_BG)
        self.cards_frame.pack(fill="both", expand=True, padx=20, pady=16)

        self.canvas = tk.Canvas(
            self.cards_frame,
            bg=COLOR_BG,
            highlightthickness=0,
        )
        self.hbar = tk.Scrollbar(self.cards_frame, orient="horizontal", command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self.cards_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.cards_frame.grid_rowconfigure(0, weight=1)
        self.cards_frame.grid_columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.status = tk.Label(
            self,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg="#35516b",
            bg=COLOR_BG,
        )
        self.status.pack(anchor="w", padx=20, pady=(0, 16))

        self._render_placeholder_cards()

    def _render_placeholder_cards(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            12,
            12,
            anchor="nw",
            text="Wybierz miasto, aby zobaczyć jednolity wykres prognozy.",
            font=("Segoe UI", 10),
            fill="#5a6c7e",
        )
        self.canvas.configure(scrollregion=(0, 0, 600, 120))

    def on_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.filtered_cities = list(self.cities)
        else:
            nq = _normalize(query)
            self.filtered_cities = [
                c for c in self.cities if nq in _normalize(c.get("name", ""))
            ]
        self.city_combo["values"] = [c["name"] for c in self.filtered_cities]
        if self.filtered_cities:
            self.city_combo.current(0)
            self.on_city_selected()
        else:
            self.status_var.set("Brak wyników. Dodaj miasto w data/cities.json.")

    def on_city_selected(self, event=None):
        name = self.city_var.get()
        if not name:
            return
        city = next((c for c in self.filtered_cities if c["name"] == name), None)
        if not city:
            self.status_var.set("Nie znaleziono miasta na liście.")
            return
        self.load_forecast(city)

    def load_forecast(self, city):
        self.status_var.set(f"Pobieram meteogram dla {city['name']}...")
        self.update_idletasks()
        try:
            img = fetch_meteogram(city["row"], city["col"])
        except Exception as exc:
            self.status_var.set(f"Nie udało się pobrać danych: {exc}")
            return

        parts = split_image_by_days(img, days=4)
        self._render_cards(parts)
        self.status_var.set(f"Prognoza dla {city['name']} gotowa.")

    def _render_cards(self, parts):
        self.canvas.delete("all")
        self._image_refs.clear()

        today = datetime.now().date()

        merged = concat_images_horizontally(parts)
        if merged is None:
            return

        header_h = 32
        day_w = merged.size[0] / max(len(parts), 1)

        for i in range(len(parts)):
            day = today + timedelta(days=i)
            x = int(i * day_w + day_w / 2)
            self.canvas.create_text(
                x,
                header_h // 2,
                text=day.strftime("%a %d.%m"),
                font=("Segoe UI", 11, "bold"),
                fill=COLOR_TEXT,
                anchor="center",
            )

        photo = ImageTk.PhotoImage(merged)
        self._image_refs.append(photo)
        self.canvas.create_image(0, header_h, image=photo, anchor="nw")
        self.canvas.configure(scrollregion=(0, 0, merged.size[0], header_h + merged.size[1]))

    def _on_canvas_resize(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all") or (0, 0, event.width, event.height))


if __name__ == "__main__":
    app = MeteoApp()
    app.mainloop()
