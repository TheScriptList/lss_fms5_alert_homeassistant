"""
Dieses Skript überwacht Fahrzeuge mit Status FMS 5 im Leitstellenspiel und steuert eine Lampe über Home Assistant entsprechend dem Status.
"""

import requests
import time
import os
import argparse
from http.cookiejar import MozillaCookieJar
from homeassistant_api import Client
from dotenv import load_dotenv, set_key
from inquirer.shortcuts import text as text_input, confirm as confirm_input, list_input

__version__ = "1.0.0"
__author__ = "L0rdEnki, MisterX2000"


LSS_API_URL = "https://www.leitstellenspiel.de/api/vehicle_states"
LSS_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.leitstellenspiel.de/"}

# Konfigurationsdatei
CONFIG_FILE = ".env"
COOKIE_FILE = "cookies.txt"
load_dotenv(CONFIG_FILE)

# Function to get all light entities
def get_all_lights(client):
    entitie_groups = client.get_entities()
    light_group = entitie_groups.get('light', {})
    return light_group.entities

def get_setting(name, message, choices = None, default = None):
    env_val = os.getenv(name)
    if env_val:
        print(f"{name} = {(env_val[:77] + '...') if len(env_val) > 80 else env_val}")
        return env_val

    if choices:
        ans = list_input(message=message, choices=choices, default = default)
    else:
        ans = text_input(message=message, default = default)

    set_key(CONFIG_FILE, name, ans)

    return ans


def load_cookies():
    if not os.path.exists(COOKIE_FILE):
        print("Fehlende cookies.txt Datei!")
        exit(1)
    cookies = MozillaCookieJar(COOKIE_FILE)
    cookies.load(ignore_discard=True, ignore_expires=True)
    return cookies


def fetch_fms5_count():
    cookies = load_cookies()
    try:
        response = requests.get(LSS_API_URL, headers=LSS_API_HEADERS, cookies=cookies)
        response.raise_for_status()
        data = response.json()
        return data.get("5", 0)
    except Exception as e:
        print(f"Fehler bei der API-Abfrage: {e}")
        return 0


def control_light(api_url, ha_token, entity_id, state, brightness=35, rgb_color=[255, 0, 0], color_temp_kelvin=None, flash=False):
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json"
    }
    data = {"entity_id": entity_id}
    if state == "turn_on":
        data["brightness"] = brightness
        if color_temp_kelvin:
            data["color_temp_kelvin"] = color_temp_kelvin
        else:
            data["rgb_color"] = rgb_color
        if flash:
            data["flash"] = "short"

    response = requests.post(f"{api_url}/services/light/{state}", headers=headers, json=data)


def get_light_state(hass_client, entity_id):
    headers = {"Authorization": f"Bearer {ha_token}"}
    response = requests.get(f"{api_url}/states/{entity_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug Modus aktivieren")
    args = parser.parse_args()
    debug_mode = args.verbose
    
    
    hass_url = get_setting("HA_API_URL", message="Bitte die Home Assistant API URL eingeben")
    hass_token = get_setting("HA_TOKEN", message="Bitte den Home Assistant API-Token eingeben")
    check_interval= get_setting("CHECK_INTERVAL", message="Bitte das Prüfintervall in Sekunden eingeben", default=10)
    
    client = Client(hass_url, hass_token)
    entity_id = get_setting("ENTITY_ID", message="Bitte die entity_id der Lampe in Home Assistant eingeben",
                             choices=[(light.state.attributes.get("friendly_name", light.entity_id), light.entity_id) for light in get_all_lights(client).values()])
    
    exit()
    
    last_fms5_count = 0
    last_light_state = client.get_entity(entity_id = entity_id)
  
    fms5_count = fetch_fms5_count()
    print(f"Die Leitstelle meldet, dass wir aktuell {fms5_count} Fahrzeuge im FMS 5 haben.")
    
    try:
        while True:
            fms5_count = fetch_fms5_count()
            if fms5_count > 0:
                control_light(api_url, ha_token, entity_id, "turn_on", brightness=35, rgb_color=[255, 0, 0])
                if fms5_count > last_fms5_count and last_fms5_count > 0:
                    time.sleep(0.5)
                    control_light(api_url, ha_token, entity_id, "turn_on", flash=True)
            else:
                if last_fms5_count == 0:
                    last_light_state = get_light_state(api_url, ha_token, entity_id)
                elif last_light_state and last_light_state.get("state") == "on":
                    control_light(api_url, ha_token, entity_id, "turn_on", brightness=last_light_state["attributes"].get("brightness", 255), 
                                  rgb_color=last_light_state["attributes"].get("rgb_color", [255, 255, 255]),
                                  color_temp_kelvin=last_light_state["attributes"].get("color_temp_kelvin"))
                else:
                    control_light(api_url, ha_token, entity_id, "turn_off")
            
            last_fms5_count = fms5_count
            
            if debug_mode:
                for i in range(check_interval, 0, -1):
                    print(f"Nächste Prüfung in {i} Sekunden.......", end="\r")
                    time.sleep(1)
                fms5_count = fetch_fms5_count()
                print(f"Aktuell haben wir {fms5_count} Fahrzeuge im FMS 5.")
            else:
                time.sleep(check_interval)
    except KeyboardInterrupt:
        if last_light_state and last_light_state.get("state") == "on":
            control_light(api_url, ha_token, entity_id, "turn_on", brightness=last_light_state["attributes"].get("brightness", 255), 
                          rgb_color=last_light_state["attributes"].get("rgb_color", [255, 255, 255]),
                          color_temp_kelvin=last_light_state["attributes"].get("color_temp_kelvin"))
        else:
            control_light(api_url, ha_token, entity_id, "turn_off")
        print("\nSkript beendet.")


if __name__ == "__main__":
    main()
