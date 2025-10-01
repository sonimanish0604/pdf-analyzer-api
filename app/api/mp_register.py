# app/routes/mp_register.py
from fastapi import APIRouter, Request, HTTPException
from app.billing.factory import get_provider
from app.services.keys import issue_api_key
from app.db import upsert_tenant_mapping

router = APIRouter()
PROVIDER = get_provider(os.environ.get("BILLING_PROVIDER", "direct"))

@router.post("/mp/register")
async def mp_register(req: Request):
    token = (await req.json()).get("token") or req.query_params.get("token")
    if not token:
        raise HTTPException(400, "Missing token")
    cust = PROVIDER.resolve_customer(token)

    tenant_id = upsert_tenant_mapping(
        provider=os.environ["BILLING_PROVIDER"],
        customer_identifier=cust.customer_identifier,
        product_code=cust.product_code,
        account_id=cust.account_id,
    )
    api_key = issue_api_key(tenant_id)  # show once
    # return minimal HTML success page
    return HTMLResponse(f"<h3>Subscription linked</h3><p>Your API key:</p><code>{api_key}</code>")
