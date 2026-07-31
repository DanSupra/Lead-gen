from typing import Dict, List
import os

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v17.0")

class MetaWebhookHandler:
    def extract_lead_ids(self, webhook_payload: Dict) -> List[Dict]:
        # payload structure: entry[] with changes[] containing leadgen_id
        leads = []
        for entry in webhook_payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                # leadgen_id is usually in value.get("leadgen_id") or value.get("leadgen_id")
                lead_id = value.get("leadgen_id") or value.get("lead_id")
                page_id = value.get("page_id") or entry.get("id")
                if lead_id:
                    leads.append({"leadgen_id": lead_id, "page_id": page_id})
        return leads

    def build_graph_url(self, leadgen_id: str, page_token: str):
        return f"https://graph.facebook.com/{GRAPH_API_VERSION}/{leadgen_id}?access_token={page_token}&fields=created_time,ad_id,form_id,field_data"
