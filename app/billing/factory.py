# app/billing/factory.py
import os

from .noop import NoopProvider

AWS_MP_ENABLED = os.getenv("AWS_MP_ENABLED", "false").lower() == "true"
AZURE_MP_ENABLED = os.getenv("AZURE_MP_ENABLED", "false").lower() == "true"
GCP_MP_ENABLED = os.getenv("GCP_MP_ENABLED", "false").lower() == "true"

# def get_provider() -> BillingProvider:
# Order of precedence; enable only one at a time for now
#    if AWS_MP_ENABLED:
#        from .aws import AWSProvider
#        return AWSProvider()
#    if AZURE_MP_ENABLED:
#        from .azure import AzureProvider  # implement later with lazy imports
#        return AzureProvider()
#    if GCP_MP_ENABLED:
#        from .gcp import GCPProvider      # implement later with lazy imports
#        return GCPProvider()
#    return NoopProvider()


def get_provider(name: str):
    name = (name or "direct").lower()
    if name == "aws":
        return AWSProvider()
    # elif name == "azure":
    #     return AzureProvider()
    # elif name == "gcp":
    #     return GCPProvider()
    else:
        return NoopProvider()
