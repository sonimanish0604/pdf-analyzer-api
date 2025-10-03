# app/billing/types.py
from typing import Any


class BillingProvider:
    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
