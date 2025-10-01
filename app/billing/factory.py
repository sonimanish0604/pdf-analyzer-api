# app/billing/factory.py
from .aws import AWSProvider
from .azure import AzureProvider
from .gcp import GCPProvider
from .direct import DirectProvider


def get_provider(name: str):
    return {
        "aws": AWSProvider(),
        "azure": AzureProvider(),
        "gcp": GCPProvider(),
        "direct": DirectProvider(),
    }[name]
