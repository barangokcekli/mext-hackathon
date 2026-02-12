"""
FastAPI server — Orchestrator Agent'ı frontend'e expose eder.

Kullanım:
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
    POST /api/orchestrate    → Tam orkestrasyon (customer + product + campaign)
    GET  /api/health         → Health check
    GET  /api/customers      → Müşteri listesi
    GET  /api/customers/:id  → Tek müşteri
"""

from __future__ import annotations

import json
import os
import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from orchestrator_agent import orchestrate_campaign, invoke_agentcore_runtime
from orchestrator_agent import CUSTOMER_SEGMENT_AGENT_ARN, PRODUCT_ANALYSIS_AGENT_ARN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MEXT Campaign Orchestrator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

ALL_CUSTOMERS = load_json(os.path.join(BASE_DIR, "customer-segment-agent", "mock-data", "farmasi", "customers-100.json"))
PRODUCT_DATA = load_json(os.path.join(BASE_DIR, "product-agent", "data", "products_2.json"))
REGIONS_DATA = load_json(os.path.join(BASE_DIR, "customer-segment-agent", "mock-data", "regions.json"))
REGION_MAP = {r["name"]: r for r in REGIONS_DATA["regions"]}
CUSTOMER_MAP = {c["customerId"]: c for c in ALL_CUSTOMERS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_customer_payload(customer: dict) -> dict:
    region_name = customer.get("region", "Marmara")
    region_info = REGION_MAP.get(region_name, REGION_MAP.get("Marmara", {}))
    return {
        "customerId": customer["customerId"],
        "city": customer["city"],
        "customer": {
            "customerId": customer["customerId"],
            "age": customer["age"],
            "gender": customer["gender"],
            "registeredAt": customer["registeredAt"] + "T00:00:00",
            "productHistory": customer["productHistory"],
        },
        "region": {
            "name": region_info.get("name", region_name),
            "climateType": region_info.get("climateType", "Temperate"),
            "medianBasket": region_info.get("medianBasket", 60.0),
            "trend": region_info.get("trend", "SKINCARE"),
        },
    }


def build_product_payload(max_products: int = 30) -> dict:
    return {
        "tenantId": PRODUCT_DATA["tenantId"],
        "products": PRODUCT_DATA["products"][:max_products],
        "orderHistory": PRODUCT_DATA.get("orderHistory", [])[:5],
        "currentMonth": PRODUCT_DATA.get("currentMonth", 2),
        "climateData": PRODUCT_DATA.get("climateData", {}),
    }


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------
class OrchestrateRequest(BaseModel):
    prompt: str = Field(default="Kişiselleştirilmiş kampanya önerileri oluştur")
    customerId: str | None = Field(default=None, description="Müşteri ID (ör: C-2001). Verilirse mock data'dan yüklenir.")
    customerData: dict | None = Field(default=None, description="Direkt müşteri verisi (customerId yerine)")
    productData: dict | None = Field(default=None, description="Direkt ürün verisi. Verilmezse products_2.json'dan yüklenir.")
    maxProducts: int = Field(default=30, description="Ürün subset boyutu")
    useLLM: bool = Field(default=True, description="True=LLM orchestrator, False=deterministik")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "agents": 4, "customers": len(ALL_CUSTOMERS), "products": len(PRODUCT_DATA["products"])}


@app.get("/api/customers")
async def list_customers():
    return [
        {
            "customerId": c["customerId"],
            "city": c["city"],
            "region": c.get("region"),
            "age": c["age"],
            "gender": c["gender"],
            "totalOrders": c.get("totalOrders"),
            "totalLifetimeValue": c.get("totalLifetimeValue"),
            "valueSegment": c.get("valueSegment"),
            "churnRisk": c.get("churnRisk"),
        }
        for c in ALL_CUSTOMERS
    ]


@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str):
    customer = CUSTOMER_MAP.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Müşteri bulunamadı: {customer_id}")
    return customer


@app.post("/api/orchestrate")
async def orchestrate(req: OrchestrateRequest):
    """Tam orkestrasyon: customer analysis → product analysis → campaign generation"""

    # Customer data
    customer_data = req.customerData
    if not customer_data and req.customerId:
        customer = CUSTOMER_MAP.get(req.customerId)
        if not customer:
            raise HTTPException(status_code=404, detail=f"Müşteri bulunamadı: {req.customerId}")
        customer_data = build_customer_payload(customer)

    # Product data
    product_data = req.productData or build_product_payload(req.maxProducts)

    logger.info("Orchestrate: prompt=%s, customer=%s, products=%d, llm=%s",
                req.prompt[:50], req.customerId or "custom", len(product_data.get("products", [])), req.useLLM)

    result = orchestrate_campaign(
        prompt=req.prompt,
        customer_data=customer_data,
        product_data=product_data,
        use_llm=req.useLLM,
    )
    return result
