# Weather_app

Prosta aplikacja desktopowa w Pythonie (Tkinter) z prognozą z meteo.pl (ICM UW).
W repozytorium jest też wersja web (Flask) gotowa do wdrożenia na Render.

## Uruchomienie (desktop)

1. Zainstaluj zależności:

```
pip install -r requirements.txt
```

2. Uruchom:

```
python main.py
```

## Uruchomienie (web, lokalnie)

1. Zainstaluj zależności:

```
pip install -r requirements.txt
```

2. Uruchom serwer:

```
python web_app.py
```

3. Otwórz w przeglądarce: `http://localhost:5000`

## Wdrożenie na Render

1. Wrzuć projekt na GitHub.
2. Na Render utwórz nowy **Web Service** z repozytorium.
3. Ustaw:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn web_app:app`
4. Po wdrożeniu Render poda link do aplikacji.

## GitHub CLI: szybka ściąga (commit → push → PR)

### Najprostszy wariant (na main)

```
git status
git add .
git commit -m "Opis zmian"
git push
gh pr create --base main --head main --title "Opis zmian" --body "Krótki opis tego, co zmieniono."
```

### Lepszy wariant (osobna gałąź)

```
git checkout -b feature/nazwa
git add .
git commit -m "Opis zmian"
git push -u origin feature/nazwa
gh pr create --base main --head feature/nazwa --title "Opis zmian" --body "Krótki opis tego, co zmieniono."
```

## Skąd dane
Aplikacja pobiera meteogramy z ICM (meteo.pl) i prezentuje je jako prognozę na kolejne dni.

## Miasta
Lista miast jest w `data/cities.json`. Jeśli chcesz dodać własne, znajdź parametry `row` i `col`
(np. z linku do meteogramu na meteo.pl) i dopisz je do listy.
