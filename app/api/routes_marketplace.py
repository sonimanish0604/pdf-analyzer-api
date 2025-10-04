# api/routes_marketplace.py
import os

import boto3
from db import upsert_tenant_mapping
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from services.keys import issue_api_key

router = APIRouter()

AWS_PRODUCT_CODE = os.getenv("AWS_PRODUCT_CODE")

# Boto3 client for Marketplace Metering
marketplace = boto3.client("meteringmarketplace")


@router.post("/register")
async def register(req: Request):
    body = await req.json()
    token = body.get("token") or req.query_params.get("token")
    if not token:
        raise HTTPException(400, "Missing AWS registration token")

    try:
        # Exchange token for customer details
        resp = marketplace.resolve_customer(RegistrationToken=token)
        customer_id = resp["CustomerIdentifier"]
        account_id = resp.get("CustomerAWSAccountId")
        product_code = resp["ProductCode"]
    except Exception as e:
        raise HTTPException(400, f"Failed to resolve customer: {str(e)}")

    # Store tenant in DB (idempotent)
    tenant_id = upsert_tenant_mapping(
        provider="aws",
        customer_identifier=customer_id,
        product_code=product_code,
        account_id=account_id,
    )

    # Issue API key (or return existing)
    api_key = issue_api_key(tenant_id)

    # Show a simple HTML page
    html = f"""
    <html>
      <head><title>Aegis PreScan Registration</title></head>
      <body style="font-family: sans-serif;">
        <h2>Subscription Linked Successfully</h2>
        <p>Your AWS Marketplace subscription is now active.</p>
        <p><b>Your API Key (copy now, shown only once):</b></p>
        <code>{api_key}</code>
        <p><a href="https://aegisprescan.io/docs">View Documentation</a></p>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
