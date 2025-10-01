# app/billing/base.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class ResolvedCustomer:
    customer_identifier: str  # marketplace-native id
    account_id: Optional[str]  # cloud account if available
    product_code: str
    email_hint: Optional[str] = None


@dataclass
class Entitlement:
    active: bool
    plan: str  # free|dev|pro|enterprise
    expires_at: Optional[int] = None


class BillingProvider:
    def resolve_customer(self, token: str) -> ResolvedCustomer: ...
    def get_entitlement(self, customer_identifier: str) -> Entitlement: ...
    def report_usage(
        self,
        customer_identifier: str,
        dimension: str,
        quantity: int,
        ts_epoch_secs: int,
    ) -> None: ...
