# app/billing/types.py
from typing import Any, Dict

class BillingProvider:
    def register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
