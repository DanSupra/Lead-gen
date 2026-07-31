from .base import Connector
import requests
from typing import Dict, List
import os
from urllib.parse import urlencode

class SocrataConnector(Connector):
    def __init__(self, domain: str, dataset_id: str, app_token: str | None = None):
        self.domain = domain  # e.g., data.cityname.gov
        self.dataset = dataset_id
        self.base = f"https://{domain}/resource/{dataset_id}.json"
        self.app_token = app_token

    def _get(self, params: Dict):
        headers = {}
        if self.app_token:
            headers['X-App-Token'] = self.app_token
        r = requests.get(self.base, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def fetch_recent(self, area: Dict[str, float], since_iso: str):
        # area example: {"lat": 40.7, "lon": -74.0, "radius_m": 2000}
        lat, lon, radius = area['lat'], area['lon'], area['radius_m']
        # Socrata supports within_circle(column, lat, lon, radius)
        # Column name may vary; allow config or fallback to 'location'
        where = f"within_circle(location, {lat}, {lon}, {radius}) AND issue_date >= '{since_iso}'"
        params = {"$where": where, "$limit": 1000, "$order": "issue_date DESC"}
        return self._get(params)

    def normalize(self, raw: Dict):
        return {
            "source": "socrata",
            "event_type": raw.get("permit_type") or raw.get("work_type"),
            "event_time": raw.get("issue_date"),
            "properties": raw,
            "geometry": raw.get("location")
        }
