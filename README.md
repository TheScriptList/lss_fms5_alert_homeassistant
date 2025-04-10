# Leitstellenspiel FMS 5 Home Assistant Light Control

[![Build Executable](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-exe.yml/badge.svg)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-exe.yml)
[![Docker Image CI](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-docker.yml/badge.svg)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-docker.yml)
[![GitHub Release](https://img.shields.io/github/v/release/TheScriptList/lss_fms5_alert_homeassistant?label=Latest%20Release)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/releases/latest)
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/TheScriptList/lss_fms5_alert_homeassistant/total?label=Total%20Downloads)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/releases)

Dieses Skript überwacht Fahrzeuge mit Status FMS 5 im Leitstellenspiel und steuert eine Lampe über Home Assistant entsprechend dem Status.

## Inhaltsverzeichnis

- [Leitstellenspiel FMS 5 Home Assistant Light Control](#leitstellenspiel-fms-5-home-assistant-light-control)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Installationsmöglichkeiten](#installationsmöglichkeiten)
    - [Nutzung der fertigen Binary](#nutzung-der-fertigen-binary)
    - [Nutzung per Docker](#nutzung-per-docker)
    - [Ausführung aus dem Quellcode](#ausführung-aus-dem-quellcode)
      - [Alternativ auch möglich mit `uv`](#alternativ-auch-möglich-mit-uv)
  - [Voraussetzungen](#voraussetzungen)
  - [Einrichtung](#einrichtung)
    - [1. Home Assistant API-Token erstellen](#1-home-assistant-api-token-erstellen)
    - [2. Home Assistant `entity_id` herausfinden (optional)](#2-home-assistant-entity_id-herausfinden-optional)
    - [3. Cookies exportieren](#3-cookies-exportieren)
    - [4. Konfigurationswerte eingeben](#4-konfigurationswerte-eingeben)
  - [Funktionsweise](#funktionsweise)
  - [Fehlerbehebung](#fehlerbehebung)
  - [Contributors](#contributors)

## Installationsmöglichkeiten

### Nutzung der fertigen Binary

1. Lade die neueste Version der ausführbaren Datei von der [Releases-Seite](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/releases/latest) herunter.
2. Speichere die Datei in einem Verzeichnis deiner Wahl.
3. Folge der Anleitung zur [Einrichtung](#einrichtung).

### Nutzung per Docker

1. Stelle sicher, dass Docker installiert ist.
2. Ziehe das Docker-Image:

   ```bash
   docker pull ghcr.io/thescriptlist/lss_fms5_alert_homeassistant:latest
   ```

3. Starte den Container:

   ```bash
   docker run -v $(pwd)/config:/app/config -v $(pwd)/cookies:/app/cookies ghcr.io/thescriptlist/lss_fms5_alert_homeassistant:latest
   ```

4. Folge der Anleitung zur [Einrichtung](#einrichtung).

### Ausführung aus dem Quellcode

1. Stelle sicher, dass Python (mindestens Version 3.13) installiert ist.
2. Klone das Repository:

   ```bash
   git clone https://github.com/TheScriptList/lss_fms5_alert_homeassistant.git
   ```

3. Installiere die Abhängigkeiten:

   ```bash
   pip install -r requirements.txt
   ```

4. Starte das Skript:

   ```bash
   python lss_fms5_alert_homeassistant.py
   ```

5. Folge der Anleitung zur [Einrichtung](#einrichtung).

#### Alternativ auch möglich mit `uv`

Falls du das Skript mit `uv` ausführen möchtest, kannst du den folgenden Befehl verwenden:

```bash
uv run lss_fms5_alert_homeassistant.py
```

Hierbei wird automatisch eine virtuelle Umgebung erstellt und aktiviert, bevor das Skript gestartet wird. Dies ist besonders nützlich, wenn du mehrere Python-Projekte mit unterschiedlichen Abhängigkeiten verwalten möchtest.  
Was `uv` ist und wie du es installierst findest du hier:
https://docs.astral.sh/uv/

## Voraussetzungen

- **Python** (mindestens Version 3.13) oder Docker.
- Die Python-Bibliotheken `requests`, `configparser`, `argparse`, `homeassistant-api`, `inquirer`, `python-dotenv`.
- **Home Assistant** mit einer steuerbaren Lampe.
- Eine Datei `cookies.txt` mit den Cookies von `leitstellenspiel.de` im Format `Netscape HTTP Cookie File`.

## Einrichtung

### 1. Home Assistant API-Token erstellen

1. In Home Assistant auf **Benutzerprofil** klicken.
2. Unter "Langzeit-Token" auf **Token erstellen** klicken.
3. Einen Namen vergeben (z. B. `Leitstellenspiel Skript`) und erstellen.
4. Den generierten Token speichern (wird nur einmal angezeigt!).

### 2. Home Assistant `entity_id` herausfinden (optional)

Dieser Schritt ist nur notwendig, wenn das Skript nicht interaktiv gestartet wird, z. B. in einem Docker-Container. Andernfalls wird die `entity_id` beim ersten Start des Skripts interaktiv abgefragt.

1. In Home Assistant unter **Entwicklerwerkzeuge** → **Zustände** gehen.
2. Die gewünschte Lampe suchen und deren `entity_id` notieren (z. B. `light.hue_lightstrip`).

### 3. Cookies exportieren

1. Einen Browser mit Cookie-Export-Funktion verwenden (z. B. Chrome mit [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) oder Firefox mit [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)).
2. Auf **leitstellenspiel.de** einloggen.
3. Die Cookies exportieren und in eine Datei `cookies.txt` speichern.

### 4. Konfigurationswerte eingeben

Beim ersten Start des Skripts werden folgende Werte abgefragt und in der `.env`-Datei gespeichert:

- `HASS_API_URL`: Die API-URL von Home Assistant.
- `HASS_API_TOKEN`: Der Home Assistant API-Token.
- `CHECK_INTERVAL`: Das Prüfintervall in Sekunden.
- `ENTITY_ID`: Die ID der zu steuernden Lampe.
- `LIGHT_BRIGHTNESS`: Die Helligkeit der Lampe (0–255).
- `LIGHT_COLOR`: Die Farbe der Lampe in RGB (z. B. `255,0,0` für Rot).

Zusätzlich kann der folgende Parameter optional gesetzt werden:

- `LOGGING_LEVEL`: Das gewünschte Log-Level. Mögliche Werte sind `DEBUG`, `INFO` (Standard) und `WARNING`.

## Funktionsweise

1. Das Skript ruft regelmäßig die Anzahl der Fahrzeuge im FMS 5 ab.
2. Falls Fahrzeuge im FMS 5 sind, wird die Lampe in der konfigurierten Farbe und Helligkeit eingeschaltet.
3. Falls neue Fahrzeuge hinzukommen, blinkt die Lampe kurz.
4. Falls keine Fahrzeuge mehr im FMS 5 sind, wird der vorherige Lichtzustand wiederhergestellt.
5. Falls das Skript mit `STRG+C` beendet wird, wird der vorherige Zustand ebenfalls wiederhergestellt.

## Fehlerbehebung

- Falls das Skript meldet, dass `cookies.txt` fehlt: Die Datei erneut exportieren und sicherstellen, dass sie im richtigen Verzeichnis liegt.
- Falls die Lampe nicht reagiert: `entity_id` und API-Token prüfen.
- Falls das Skript unerwartet beendet wird, prüfen, ob die Home Assistant URL korrekt ist.
- Falls ihr Probleme mit dem Skript habt, kommentiert gerne im Repository. Achtet darauf, dass ihr **niemals** den Home Assistant Token (`HASS_API_TOKEN`) oder den Inhalt der `cookies.txt` teilt.

## Contributors

Dieses Skript wurde von [L0rdEnki](https://github.com/L0rdEnki) und [MisterX2000](https://github.com/MisterX2000) erstellt. Wir hoffen, es gefällt euch.
