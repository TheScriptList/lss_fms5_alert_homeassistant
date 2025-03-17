#!/usr/bin/env python3
"""
Dieses Skript überwacht Fahrzeuge mit Status FMS 5 im Leitstellenspiel und steuert eine Lampe über Home Assistant entsprechend dem Status.
"""

import requests
import os
import logging
from time import sleep
from urllib.parse import urlparse
from http.cookiejar import MozillaCookieJar
from homeassistant_api import Client
from dotenv import load_dotenv, set_key
from inquirer.shortcuts import text as text_input, confirm as confirm_input, list_input

__version__ = "1.0.0"
__author__ = "L0rdEnki, MisterX2000"

LSS_API_URL = "https://www.leitstellenspiel.de/api/vehicle_states"
HASS_TEMP_SCENE = "lss_fms5_alert_temp_scene"

# Konfigurationsdatei
CONFIG_FILE = ".env"
COOKIE_FILE = "cookies.txt"

# Objekte Initialisieren
log = logging.getLogger(__name__)

# Function to get all light entities
def get_setting(name, message, choices = None, default = None):
    env_val = os.getenv(name)
    if env_val:
        log.info(f"{name} = {(env_val[:77] + '...') if len(env_val) > 80 else env_val}")
        return env_val

    if choices:
        ans = list_input(message=message, choices=choices, default = default)
    else:
        ans = text_input(message=message, default = default)

    set_key(CONFIG_FILE, name, ans)

    return ans

def load_cookies(file_path):
    cookie_jar = MozillaCookieJar()
    try:
        cookie_jar.load(file_path, ignore_discard=True, ignore_expires=True)
    except FileNotFoundError:
        log.error(COOKIE_FILE + " nicht gefunden")
        exit(1)
    return cookie_jar

def get_all_lights(client):
    entitie_groups = client.get_entities()
    light_group = entitie_groups.get("light", {})
    return light_group.entities

def fetch_fms5_count():
    try:
        response = requests.get(LSS_API_URL, cookies=COOKIES)
        response.raise_for_status()
        data = response.json()
        return data.get("5", 0)
    except Exception as e:
        log.error(f"Fehler bei der LSS-API-Abfrage: {e}")
        return 0


if __name__ == "__main__":
    # Einstellungen aus der Environment laden
    load_dotenv(CONFIG_FILE)

    # Logging einrichten
    logging.basicConfig(
        level=os.getenv("LOGGING_LEVEL", "INFO"),
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s")
    log.info("v" + str(__version__))

    HASS_URL = urlparse(get_setting("HASS_API_URL", message="Bitte die Home Assistant API URL eingeben"))
    HASS_URL = HASS_URL._replace(path="/api").geturl() # /api Pfad hinzufügen, falls fehlend
    HASS_TOKEN = str(get_setting("HASS_API_TOKEN", message="Bitte den Home Assistant API-Token eingeben"))
    CHECK_INTERVAL = int(get_setting("CHECK_INTERVAL", message="Bitte das Prüfintervall in Sekunden eingeben", default=10))
    LIGHT_BRIGHTNESS = int(get_setting("LIGHT_BRIGHTNESS", message="Helligkeit der Lampe [0-255]", default=50))
    LIGHT_COLOR = str(get_setting("LIGHT_COLOR", message="Farbe der Lampe in RGB [0-255,0-255,0-255]", default="255,0,0"))
    LIGHT_COLOR = LIGHT_COLOR.split(",")
    COOKIES = load_cookies(COOKIE_FILE)

    # HASS Client einrichten
    client = Client(HASS_URL, HASS_TOKEN)
    entity_id = get_setting("ENTITY_ID", message="Bitte die entity_id der Lampe in Home Assistant eingeben",
                             choices=[(light.state.attributes.get("friendly_name", light.entity_id), light.entity_id) for light in get_all_lights(client).values()])
    light = client.get_domain("light")
    scene = client.get_domain("scene")
    
    last_fms5_count = 0
    scene.create(scene_id=HASS_TEMP_SCENE, snapshot_entities=entity_id) # Temp Scene zum wiederherstellen erstellen
    
    try:
        while True:
            fms5_count = fetch_fms5_count()
            log.info(f"Aktuelle FMS5 Anzahl: {fms5_count}")
            if fms5_count > 0:
                light.turn_on(entity_id, brightness=LIGHT_BRIGHTNESS, rgb_color=LIGHT_COLOR)
                if fms5_count > last_fms5_count and last_fms5_count > 0:
                    sleep(0.5)
                    light.turn_on(entity_id, flash="short")
            else:
                if last_fms5_count == 0:
                    # Temp Scene zum wiederherstellen aktualisieren, falls keine FMS5
                    scene.create(scene_id=HASS_TEMP_SCENE, snapshot_entities=entity_id)
                else:
                    scene.turn_on(entity_id=f"scene.{HASS_TEMP_SCENE}")
            
            last_fms5_count = fms5_count
            
            log.debug(f"Nächste Prüfung in {CHECK_INTERVAL} Sekunden.......")
            sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        # Restore the light to its original state and cleanup
        log.info("KeyboardInterrupt festgestellt, stelle Ursprungszustand wieder her...")
        scene.turn_on(entity_id=f"scene.{HASS_TEMP_SCENE}")
        scene.delete(entity_id=f"scene.{HASS_TEMP_SCENE}")
