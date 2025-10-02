# app/billing/noop.py
from typing import Any, Dict
from .types import BillingProvider

class NoopProvider(BillingProvider):
    def register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "noop", "message": "Marketplace disabled", "echo": payload}