# app/billing/base.py
from dataclasses import dataclass


@dataclass
class ResolvedCustomer:
    customer_identifier: str  # marketplace-native id
    account_id: str | None  # cloud account if available
    product_code: str
    email_hint: str | None = None


@dataclass
class Entitlement:
    active: bool
    plan: str  # free|dev|pro|enterprise
    expires_at: int | None = None


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
