# Leitstellenspiel FMS 5 Home Assistant Light Control

[![Build Executable](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-exe.yml/badge.svg)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-exe.yml)
[![Docker Image CI](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-docker.yml/badge.svg)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/actions/workflows/build-docker.yml)
[![GitHub Release](https://img.shields.io/github/v/release/TheScriptList/lss_fms5_alert_homeassistant?label=Latest%20Release)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/releases/latest)
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/TheScriptList/lss_fms5_alert_homeassistant/total?label=Total%20Downloads)](https://github.com/TheScriptList/lss_fms5_alert_homeassistant/releases)


Dieses Skript überwacht Fahrzeuge mit Status FMS 5 im Leitstellenspiel und steuert eine Lampe über Home Assistant entsprechend dem Status.

> [!IMPORTANT]
> Die Anleitung sowie das Script sind noch WIP und nicht Final!

## Inhaltsverzeichnis

- [Leitstellenspiel FMS 5 Home Assistant Light Control](#leitstellenspiel-fms-5-home-assistant-light-control)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Roadmap](#roadmap)
  - [Voraussetzungen](#voraussetzungen)
  - [Einrichtung](#einrichtung)
  - [Nutzung](#nutzung)
  - [Funktionsweise](#funktionsweise)
  - [Anpassungen für andere Farben und Helligkeit](#anpassungen-für-andere-farben-und-helligkeit)
  - [Fehlerbehebung](#fehlerbehebung)
  - [Contributors](#contributors)

## Roadmap

- [ ]  Aus der Python Datei eine ausführbare .exe Datei machen.

## Voraussetzungen

### Notwendige Software und Abhängigkeiten <!-- omit from toc -->

- **Python** (mindestens Version 3.7) muss installiert sein: [[Python herunterladen](https://www.python.org/downloads/)]
- Die Python-Bibliotheken `requests`, `configparser` und `argparse` müssen installiert sein. Falls noch nicht vorhanden, installiere sie mit:
  ```bash
  pip install requests configparser argparse
  ```
- **Home Assistant** muss eingerichtet sein und eine steuerbare Lampe enthalten.

### Notwendige Informationen <!-- omit from toc -->

- Eine **Home Assistant API URL** (Standard: `http://homeassistant.local:8123/api`, alternativ kann `homeassistant.local` durch die IP-Adresse ersetzt werden auf der Home Assistant läuft, z.B. `http://192.168.178.2:8123/api`)
- Ein **Home Assistant API-Token** (siehe Anleitung unten zur Erstellung)
- Die **`entity_id`** der zu steuernden Lampe (z.B. `light.hue_lightstrip`)

## Einrichtung

### 1. Speichern des Skripts <!-- omit from toc -->

Die Datei `lss_fms5_alert_homeassistant.py` einfach speichern und wie unten beschrieben starten.
Es wird empfohlen, das Skript in einem dedizierten Verzeichnis zu speichern, um eine übersichtliche Struktur zu gewährleisten, insbesondere wenn die `config.ini` und `cookies.txt` Dateien darin enthalten sind.



### 2. Home Assistant API-Token erstellen <!-- omit from toc -->

1. In Home Assistant auf **Benutzerprofil** klicken.
2. Unter "Langzeit-Token" auf **Token erstellen** klicken.
3. Einen Namen vergeben (z.B. `Leitstellenspiel Skript`) und erstellen.
4. Den generierten Token speichern (wird nur einmal angezeigt!).

### 3. Home Assistant `entity_id` herausfinden <!-- omit from toc -->

1. In Home Assistant unter **Entwicklerwerkzeuge** → **Zustände** gehen.
2. Die gewünschte Lampe suchen und deren `entity_id` notieren (z. B. `light.hue_lightstrip`).

### 4. Cookies als `cookies.txt` speichern <!-- omit from toc -->

1. Einen Browser mit Cookie-Export-Funktion verwenden (z. B. Chrome mit [[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)] oder Firefox mit [[cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)]).
2. Auf **leitstellenspiel.de** einloggen.
3. Die Cookies exportieren und in eine Datei `cookies.txt` speichern.
4. Das Format muss `Netscape HTTP Cookie File` sein (eine Zeile pro Cookie, tab-getrennt).

### 5. Konfigurationswerte in `config.ini` <!-- omit from toc -->

Beim ersten Start des Skripts werden folgende Werte abgefragt und in der `config.ini` gespeichert:

- `HA_API_URL`: Die API-URL von Home Assistant.
- `HA_TOKEN`: Der Home Assistant API-Token.
- `CHECK_INTERVAL`: Das Prüfintervall in Sekunden.
- `ENTITY_ID`: Die ID der zu steuernden Lampe.

## Nutzung

Das Skript wird im Normalmodus gestartet, außer es wird mit `-v` für den Debug-Modus aufgerufen:

```bash
python lss_fms5_alert_homeassistant.py
```

Debug-Modus aktivieren:

```bash
python lss_fms5_alert_homeassistant.py -v
```

Beim ersten Start werden die API-URL, der API-Token, die `entity_id` und das Prüfintervall abgefragt und in `config.ini` gespeichert.

### Unterschiede zwischen Normal- und Debug-Modus <!-- omit from toc -->

- **Normalmodus:** Minimalistische Ausgabe, zu Beginn wird die aktuelle Anzahl der Fahrzeuge im FMS 5 ausgegeben, danach erfolgen keine Ausgaben mehr.
- **Debug-Modus:** Zeigt einen Countdown bis zur nächsten Statusprüfung und gibt fortlaufend den aktuellen FMS-5-Status aus.

## Funktionsweise

1. Das Skript ruft regelmäßig die Anzahl der Fahrzeuge im FMS 5 ab.
2. Falls Fahrzeuge im FMS 5 sind, wird die Lampe in Rot mit 35 Helligkeit eingeschaltet.
3. Falls neue Fahrzeuge hinzukommen, blinkt die Lampe kurz.
4. Falls keine Fahrzeuge mehr im FMS 5 sind, wird die vorherige Lichtfarbe, Helligkeit und der Zustand wiederhergestellt.
5. Falls das Skript mit `STRG+C` beendet wird, wird der vorherige Zustand ebenfalls wiederhergestellt.

## Anpassungen für andere Farben und Helligkeit

Falls eine andere Farbe als **Rot** (`[255, 0, 0]`) oder eine andere Helligkeit als **35** gewünscht wird, müssen die folgenden Zeilen im Skript angepasst werden:

- **Standard-Farbe und Helligkeit beim Einschalten der Lampe:**

  ```python
  control_light(api_url, ha_token, entity_id, "turn_on", brightness=35, rgb_color=[255, 0, 0])
  ```

  → Hier kann `brightness=35` durch einen anderen Wert (0–255) ersetzt werden.
  → `rgb_color=[255, 0, 0]` kann auf eine andere RGB-Farbe geändert werden, z. B. Blau `[0, 0, 255]`.

- **Wenn keine FMS-5-Fahrzeuge mehr vorhanden sind:**

  ```python
  control_light(api_url, ha_token, entity_id, "turn_on", brightness=last_light_state["attributes"].get("brightness", 255), 
                rgb_color=last_light_state["attributes"].get("rgb_color", [255, 255, 255]),
                color_temp_kelvin=last_light_state["attributes"].get("color_temp_kelvin"))
  ```

  → Falls die vorherige Helligkeit ignoriert werden soll, kann `brightness=255` fest eingestellt werden.

Nach diesen Änderungen einfach das Skript speichern und erneut ausführen.

## Fehlerbehebung

- Ich nutze das Skript mit einer Philips Hue Lampe, die über Home Assistant gesteuert wird. Falls ihr andere Leuchtmittel nutzt, kann es sein, dass ihr das Skript anpassen müsst, da andere Lampen unter Umständen andere Parameter mitgeben, die zum Steuern notwendig sind.
- Falls das Skript meldet, dass `cookies.txt` fehlt: Die Datei erneut exportieren und sicherstellen, dass sie im richtigen Verzeichnis liegt.
- Falls die Lampe nicht reagiert: `entity_id` und API-Token prüfen.
- Falls das Skript unerwartet beendet wird, prüfen, ob die Home Assistant URL korrekt ist.
- Falls ihr Probleme mit dem Skript, kommentiert hier gerne und wir versuchen euch zu helfen. Aber bitte achtet darauf, dass ihr <ins>**niemals**</ins> den Home Assistant Token (`ha_token`) teilt. Auch solltet ihr <ins>**niemals**</ins> den Inhalt der `cookies.txt` teilen, da man mit dieser Datei euren LSS Account übernehmen könnte.

## Contributors

Dieses Skript wurde von [L0rdEnki](https://github.com/L0rdEnki) und [MisterX2000](https://github.com/MisterX2000) erstellt. Wir hoffen, es gefällt euch.
