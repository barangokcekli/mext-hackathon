"""
FastAPI server — Mock data ile kampanya üretimi (Strands SDK olmadan)

Kullanım:
    python3 -m uvicorn api_server_simple:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
    POST /api/orchestrate    → Mock kampanya üretimi
    GET  /api/health         → Health check
    GET  /api/customers      → Müşteri listesi
    GET  /api/customers/:id  → Tek müşteri

Not: Bu versiyon DynamoDB'den veri çekebilir ama AgentCore Runtime kullanmaz.
"""

from __future__ import annotations

import json
import os
import logging
from typing import Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import orchestrator wrapper for real agents
USE_REAL_AGENTS = os.environ.get("USE_REAL_AGENTS", "false").lower() == "true"
orchestrator_wrapper = None

if USE_REAL_AGENTS:
    try:
        from orchestrator_wrapper import orchestrate_campaign_deterministic
        orchestrator_wrapper = orchestrate_campaign_deterministic
        logger.info("✓ Real AgentCore Runtime agents enabled")
    except Exception as e:
        logger.warning(f"Failed to load orchestrator wrapper: {e}")
        USE_REAL_AGENTS = False

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
# DynamoDB Support (optional)
# ---------------------------------------------------------------------------
USE_DYNAMODB = os.environ.get("USE_DYNAMODB", "false").lower() == "true"
dynamodb_customer_client = None
dynamodb_product_client = None

if USE_DYNAMODB:
    try:
        import sys
        import importlib.util
        
        # Customer DynamoDB client
        customer_spec = importlib.util.spec_from_file_location(
            "customer_dynamodb_client",
            os.path.join(BASE_DIR, "customer-segment-agent", "dynamodb_client.py")
        )
        customer_module = importlib.util.module_from_spec(customer_spec)
        customer_spec.loader.exec_module(customer_module)
        
        # Product DynamoDB client
        product_spec = importlib.util.spec_from_file_location(
            "product_dynamodb_client",
            os.path.join(BASE_DIR, "product-agent", "dynamodb_client.py")
        )
        product_module = importlib.util.module_from_spec(product_spec)
        product_spec.loader.exec_module(product_module)
        
        dynamodb_customer_client = customer_module.DynamoDBClient(region_name="us-west-2")
        dynamodb_product_client = product_module.ProductDynamoDBClient(region_name="us-west-2")
        logger.info("✓ DynamoDB clients initialized")
    except Exception as e:
        logger.warning(f"DynamoDB initialization failed: {e}")
        USE_DYNAMODB = False


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


def generate_mock_campaign(prompt: str, customer_data: Optional[dict], product_data: dict) -> dict:
    """Mock kampanya üretimi"""
    
    # Customer insight
    customer_insight = None
    if customer_data:
        customer_insight = {
            "customerId": customer_data.get("customerId"),
            "city": customer_data.get("city"),
            "age": customer_data["customer"]["age"],
            "gender": customer_data["customer"]["gender"],
            "ageSegment": "YOUNG_ADULT" if customer_data["customer"]["age"] < 30 else "ADULT",
            "valueSegment": "HIGH_VALUE" if customer_data["customer"].get("totalLifetimeValue", 0) > 1000 else "REGULAR",
            "churnSegment": "LOW_RISK",
            "loyaltyTier": "GOLD",
            "affinityCategory": customer_data["region"].get("trend", "SKINCARE"),
            "affinityType": "STRONG",
            "region": customer_data["region"]["name"],
            "climateType": customer_data["region"]["climateType"]
        }
    
    # Product insight
    products = product_data.get("products", [])
    product_insight = {
        "totalProducts": len(products),
        "heroProducts": products[:5] if products else [],
        "slowMovers": products[-3:] if len(products) > 3 else [],
        "seasonalProducts": [p for p in products if "Kış" in p.get("productName", "") or "Winter" in p.get("productName", "")][:3]
    }
    
    # Analyze prompt for campaign type
    is_aggressive = any(word in prompt.lower() for word in ["agresif", "hızlı", "stok", "fazla", "aggressive"])
    is_seasonal = any(word in prompt.lower() for word in ["kış", "yaz", "bahar", "sonbahar", "winter", "summer"])
    
    # Generate campaigns based on prompt
    campaigns = []
    
    if is_aggressive:
        # Aggressive stock clearance campaign
        slow_movers = [p for p in products if p.get("stock", 0) > 100 or p.get("lifecycleStage") == "DECLINING"][:10]
        campaigns.append({
            "campaignId": f"CAMP-{datetime.now().strftime('%Y%m%d')}-001",
            "campaignName": "⚡ Hızlı Stok Eritme Kampanyası",
            "title": "Agresif Stok Eritme - Sınırlı Süre",
            "description": f"{prompt}\n\nFazla stoktaki ürünlerde %40'a varan indirimler. Stoklar tükenene kadar geçerli!",
            "targetCustomerSegment": "ALL_CUSTOMERS",
            "targetProductSegment": ", ".join([p["productName"] for p in slow_movers[:5]]),
            "timing": {
                "startDate": datetime.now().strftime("%Y-%m-%d"),
                "endDate": (datetime.now().replace(day=28) if datetime.now().day < 28 else datetime.now()).strftime("%Y-%m-%d"),
                "specialEvent": "Stok Eritme"
            },
            "discountSuggestion": {
                "type": "PERCENTAGE",
                "value": 40,
                "description": "%40 indirim - Stoklar tükenene kadar"
            },
            "products": [p["productName"] for p in slow_movers],
            "estimatedRevenue": sum(p.get("basePrice", 0) * 0.6 for p in slow_movers) * 50,  # 50 units estimate
            "validUntil": (datetime.now().replace(day=28) if datetime.now().day < 28 else datetime.now()).strftime("%Y-%m-%d")
        })
    
    if is_seasonal or not is_aggressive:
        # Seasonal or regular campaign
        seasonal_products = [p for p in products if p.get("isSeasonal", False)][:8]
        if not seasonal_products:
            seasonal_products = products[:8]
        
        campaigns.append({
            "campaignId": f"CAMP-{datetime.now().strftime('%Y%m%d')}-002",
            "campaignName": "🎁 Özel Sezon Kampanyası" if is_seasonal else "💎 Premium Ürün Kampanyası",
            "title": "Kış Özel Kampanyası" if "kış" in prompt.lower() or "winter" in prompt.lower() else "Özel Kampanya",
            "description": f"{prompt}\n\nSeçili ürünlerde özel fiyatlar ve hediyeler!",
            "targetCustomerSegment": customer_insight.get("valueSegment", "ALL") if customer_insight else "ALL",
            "targetProductSegment": ", ".join([p["productName"] for p in seasonal_products[:5]]),
            "timing": {
                "startDate": datetime.now().strftime("%Y-%m-%d"),
                "endDate": "2025-03-31",
                "specialEvent": "Sezon Kampanyası" if is_seasonal else None
            },
            "discountSuggestion": {
                "type": "PERCENTAGE",
                "value": 25,
                "description": "%25 indirim + Hediye"
            },
            "products": [p["productName"] for p in seasonal_products],
            "estimatedRevenue": sum(p.get("basePrice", 0) * 0.75 for p in seasonal_products) * 30,
            "validUntil": "2025-03-31"
        })
    
    # Add personalized campaign if customer data exists
    if customer_insight:
        hero_products = products[:5]
        campaigns.append({
            "campaignId": f"CAMP-{datetime.now().strftime('%Y%m%d')}-003",
            "campaignName": f"👤 {customer_insight['city']} Özel Kampanya",
            "title": f"Size Özel: {customer_insight['affinityCategory']} Ürünleri",
            "description": f"Sizin için seçtiğimiz {customer_insight['affinityCategory']} kategorisindeki premium ürünler.",
            "targetCustomerSegment": f"{customer_insight['valueSegment']} - {customer_insight['loyaltyTier']}",
            "targetProductSegment": ", ".join([p["productName"] for p in hero_products]),
            "timing": {
                "startDate": datetime.now().strftime("%Y-%m-%d"),
                "endDate": "2025-03-15",
                "specialEvent": "Kişiye Özel"
            },
            "discountSuggestion": {
                "type": "PERCENTAGE",
                "value": 20,
                "description": f"%20 sadakat indirimi - {customer_insight['loyaltyTier']} üyelerine özel"
            },
            "products": [p["productName"] for p in hero_products],
            "estimatedRevenue": sum(p.get("basePrice", 0) * 0.8 for p in hero_products) * 20,
            "validUntil": "2025-03-15"
        })
    
    return {
        "customerInsight": customer_insight,
        "productInsight": product_insight,
        "campaigns": campaigns,
        "orchestrationSummary": {
            "customerAnalyzed": customer_insight is not None,
            "productAnalyzed": True,
            "campaignCount": len(campaigns),
            "warnings": [
                "Demo Mode: Mock kampanya üretimi kullanılıyor",
                "Gerçek AI agent'ları için AgentCore Runtime'a deploy gerekli"
            ]
        }
    }


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------
class OrchestrateRequest(BaseModel):
    prompt: str = Field(default="Kişiselleştirilmiş kampanya önerileri oluştur")
    customerId: Optional[str] = Field(default=None, description="Müşteri ID (ör: C-2001)")
    customerData: Optional[dict] = Field(default=None, description="Direkt müşteri verisi")
    productData: Optional[dict] = Field(default=None, description="Direkt ürün verisi")
    maxProducts: int = Field(default=30, description="Ürün subset boyutu")
    useLLM: bool = Field(default=False, description="Mock mode'da kullanılmaz")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mode": "agentcore" if USE_REAL_AGENTS else ("dynamodb" if USE_DYNAMODB else "mock"),
        "customers": len(ALL_CUSTOMERS),
        "products": len(PRODUCT_DATA["products"]),
        "dynamodb_enabled": USE_DYNAMODB,
        "real_agents_enabled": USE_REAL_AGENTS
    }


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
    """Kampanya üretimi (Real AgentCore Runtime veya Mock)"""

    # Customer data - DynamoDB'den veya mock'tan
    customer_data = req.customerData
    if not customer_data and req.customerId:
        if USE_DYNAMODB and dynamodb_customer_client:
            try:
                customer_data = dynamodb_customer_client.build_customer_payload(req.customerId)
                logger.info(f"✓ Customer loaded from DynamoDB: {req.customerId}")
            except Exception as e:
                logger.warning(f"DynamoDB customer fetch failed: {e}, falling back to mock")
        
        if not customer_data:
            customer = CUSTOMER_MAP.get(req.customerId)
            if not customer:
                raise HTTPException(status_code=404, detail=f"Müşteri bulunamadı: {req.customerId}")
            customer_data = build_customer_payload(customer)

    # Product data - DynamoDB'den veya mock'tan
    product_data = req.productData
    if not product_data:
        if USE_DYNAMODB and dynamodb_product_client:
            try:
                product_data = dynamodb_product_client.build_product_payload(tenant_id="farmasi")
                logger.info(f"✓ Products loaded from DynamoDB: {len(product_data.get('products', []))} items")
            except Exception as e:
                logger.warning(f"DynamoDB product fetch failed: {e}, falling back to mock")
        
        if not product_data:
            product_data = build_product_payload(req.maxProducts)

    mode = "AgentCore Runtime" if USE_REAL_AGENTS else ("DynamoDB" if USE_DYNAMODB else "Mock")
    logger.info("Orchestrate: prompt=%s, customer=%s, products=%d, mode=%s",
                req.prompt[:50], req.customerId or "custom", 
                len(product_data.get("products", [])), mode)

    # Use real agents if available
    if USE_REAL_AGENTS and orchestrator_wrapper:
        try:
            result = orchestrator_wrapper(req.prompt, customer_data, product_data)
            if not result["orchestrationSummary"]["warnings"]:
                result["orchestrationSummary"]["warnings"] = ["AgentCore Runtime: Gerçek AI agent'ları kullanıldı"]
            return result
        except Exception as e:
            logger.error(f"AgentCore Runtime error: {e}, falling back to mock")
            # Fall through to mock mode
    
    # Mock mode
    result = generate_mock_campaign(req.prompt, customer_data, product_data)
    
    # Update warning based on data source
    if USE_DYNAMODB:
        result["orchestrationSummary"]["warnings"] = [
            "DynamoDB Mode: Gerçek veriler kullanılıyor",
            "AI kampanya üretimi için AgentCore Runtime'a deploy gerekli"
        ]
    
    return result
