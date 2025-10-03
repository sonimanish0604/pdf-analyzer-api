# app/billing/noop.py
from typing import Any

from .types import BillingProvider


class NoopProvider(BillingProvider):
    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "noop", "message": "Marketplace disabled", "echo": payload}
