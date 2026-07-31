from abc import ABC, abstractmethod
from typing import Any, Dict, List

class Connector(ABC):
    name: str

    @abstractmethod
    def fetch_recent(self, area: Dict[str, float], since_iso: str) -> List[Dict[str, Any]]:
        """Fetch recent events for area (e.g. bbox or lat/lon+radius)."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw payload to common signal schema"""
        raise NotImplementedError
