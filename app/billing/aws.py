# app/billing/aws.py
import boto3
import os
import time
from .base import BillingProvider, ResolvedCustomer, Entitlement


class AWSProvider(BillingProvider):
    def __init__(self):
        self.market = boto3.client(
            "awsmarketplacecommerceanalytics"
        )  # for analytics (optional)
        self.meter = boto3.client("meteringmarketplace")
        self.ent = boto3.client("marketplaceentitlementservice")
        self.prod_code = os.environ["AWS_PRODUCT_CODE"]
        self.reg = boto3.client("marketplacemetering")  # ResolveCustomer lives here

    def resolve_customer(self, token: str) -> ResolvedCustomer:
        r = self.reg.resolve_customer(RegistrationToken=token)
        return ResolvedCustomer(
            customer_identifier=r["CustomerIdentifier"],
            account_id=r.get("CustomerAWSAccountId"),
            product_code=r["ProductCode"],
        )

    def get_entitlement(self, customer_identifier: str) -> Entitlement:
        r = self.ent.get_entitlements(
            ProductCode=self.prod_code,
            Filter={"CUSTOMER_IDENTIFIER": [customer_identifier]},
        )
        active = len(r.get("Entitlements", [])) > 0
        plan = (r["Entitlements"][0].get("Dimension") if active else "free") or "free"
        return Entitlement(active=active, plan=plan)

    def report_usage(
        self,
        customer_identifier: str,
        dimension: str,
        quantity: int,
        ts_epoch_secs: int,
    ) -> None:
        self.meter.batch_meter_usage(
            ProductCode=self.prod_code,
            UsageRecords=[
                {
                    "Timestamp": time.gmtime(ts_epoch_secs),
                    "CustomerIdentifier": customer_identifier,
                    "Dimension": dimension,
                    "Quantity": quantity,
                    "UsageRecordId": f"{customer_identifier}:{dimension}:{ts_epoch_secs}",
                }
            ],
        )
