from .base import Connector
import requests
from typing import Dict, List

class NWSConnector(Connector):
    BASE = "https://api.weather.gov/alerts"
    def fetch_recent(self, area: Dict[str, float], since_iso: str):
        # area could be point or bbox. Use point search if lat/lon provided.
        lat, lon = area.get("lat"), area.get("lon")
        if lat and lon:
            url = f"{self.BASE}?point={lat},{lon}"
        else:
            # fallback: global recent alerts (use zone or area=)
            url = self.BASE
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("features", [])

    def normalize(self, raw):
        props = raw.get("properties", {})
        return {
            "source": "nws",
            "event_type": props.get("event"),
            "event_time": props.get("sent"),
            "properties": props,
            "geometry": raw.get("geometry")
        }
