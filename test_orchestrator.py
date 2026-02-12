"""
Orchestrator Agent test script — gerçek mock data ile.

Kullanım:
    python test_orchestrator.py                # Deterministik mod, C-1001
    python test_orchestrator.py --customer C-1003  # Belirli müşteri
    python test_orchestrator.py --all          # Tüm müşteriler
"""

import json
import sys
import os

# ---------------------------------------------------------------------------
# Mock data'dan gerçek test verisi oluştur
# ---------------------------------------------------------------------------

MOCK_DIR = os.path.join(os.path.dirname(__file__), "mock-data", "farmasi")

with open(os.path.join(MOCK_DIR, "customers.json"), "r", encoding="utf-8") as f:
    ALL_CUSTOMERS = json.load(f)

with open(os.path.join(MOCK_DIR, "products.json"), "r", encoding="utf-8") as f:
    RAW_PRODUCTS = json.load(f)

REGIONS_FILE = os.path.join(os.path.dirname(__file__), "mock-data", "regions.json")
with open(REGIONS_FILE, "r", encoding="utf-8") as f:
    REGIONS_DATA = json.load(f)

REGION_MAP = {r["name"]: r for r in REGIONS_DATA["regions"]}


def build_customer_payload(customer: dict) -> dict:
    """customers.json formatını customer segment agent payload'ına dönüştürür."""
    region_name = customer.get("region", "Marmara")
    region_info = REGION_MAP.get(region_name, REGION_MAP["Marmara"])

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
            "name": region_info["name"],
            "climateType": region_info["climateType"],
            "medianBasket": region_info["medianBasket"],
            "trend": region_info["trend"],
        },
    }


def build_product_payload() -> dict:
    """products.json formatını product analysis agent payload'ına dönüştürür."""
    products = []
    for p in RAW_PRODUCTS:
        stock = p.get("currentStock", 0)
        sales_30d = p.get("last30DaysSales", 0)
        trend_score = min(99, int((sales_30d / max(stock, 1)) * 500)) if stock > 0 else 10

        is_seasonal = p.get("season", "all") != "all"
        season_code = p.get("season", "all").upper() if is_seasonal else "all"

        if sales_30d > 100:
            lifecycle = "MATURE"
        elif sales_30d > 50:
            lifecycle = "GROWING"
        elif sales_30d > 20:
            lifecycle = "NEW"
        else:
            lifecycle = "DECLINING"

        products.append({
            "productId": p["productId"],
            "productName": p["productName"],
            "category": p["category"],
            "brand": "Farmasi",
            "basePrice": p["unitPrice"],
            "cost": p["unitCost"],
            "stock": stock,
            "trendScore": trend_score,
            "lifecycleStage": lifecycle,
            "isSeasonal": is_seasonal,
            "seasonCode": season_code,
            "seasonalityRules": [],
        })

    # Basit order history oluştur (son 90 gün simülasyonu)
    order_history = []
    for i, p in enumerate(RAW_PRODUCTS):
        sales = p.get("last30DaysSales", 0)
        if sales > 0:
            order_history.append({
                "orderId": f"O-{9000+i}",
                "items": [{"productId": p["productId"], "quantity": sales}],
            })

    climate_data = {
        "Istanbul": {"avgTempC": 7, "humidityPct": 78, "rainfallMm": 90, "seasonTag": "WINTER"},
        "Ankara": {"avgTempC": 2, "humidityPct": 65, "rainfallMm": 40, "seasonTag": "WINTER"},
        "Izmir": {"avgTempC": 10, "humidityPct": 70, "rainfallMm": 100, "seasonTag": "WINTER"},
        "Antalya": {"avgTempC": 12, "humidityPct": 68, "rainfallMm": 180, "seasonTag": "WINTER"},
        "Trabzon": {"avgTempC": 5, "humidityPct": 80, "rainfallMm": 70, "seasonTag": "WINTER"},
        "Bursa": {"avgTempC": 6, "humidityPct": 75, "rainfallMm": 85, "seasonTag": "WINTER"},
        "Gaziantep": {"avgTempC": 5, "humidityPct": 60, "rainfallMm": 55, "seasonTag": "WINTER"},
    }

    return {
        "tenantId": "farmasi",
        "products": products,
        "orderHistory": order_history,
        "currentMonth": 2,
        "climateData": climate_data,
    }


def main():
    from orchestrator_agent import orchestrate_campaign

    # Parse args
    customer_id = "C-1001"
    run_all = "--all" in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == "--customer" and i + 1 < len(sys.argv):
            customer_id = sys.argv[i + 1]

    product_payload = build_product_payload()

    if run_all:
        customers_to_test = ALL_CUSTOMERS
    else:
        customers_to_test = [c for c in ALL_CUSTOMERS if c["customerId"] == customer_id]
        if not customers_to_test:
            print(f"Müşteri bulunamadı: {customer_id}")
            print(f"Mevcut müşteriler: {[c['customerId'] for c in ALL_CUSTOMERS]}")
            return

    for customer in customers_to_test:
        customer_payload = build_customer_payload(customer)

        prompt = "Kış sezonu için bu müşteriye özel kişiselleştirilmiş kampanya önerileri oluştur"

        print(f"\n{'='*70}")
        print(f"  Müşteri: {customer['customerId']} | {customer['city']} | "
              f"Yaş: {customer['age']} | Cinsiyet: {customer['gender']}")
        print(f"  Ürün geçmişi: {len(customer['productHistory'])} ürün")
        print(f"  Ürün kataloğu: {len(product_payload['products'])} ürün")
        print(f"{'='*70}")

        result = orchestrate_campaign(
            prompt=prompt,
            customer_data=customer_payload,
            product_data=product_payload,
            use_llm=False,
        )

        # Özet yazdır
        summary = result.get("orchestrationSummary", {})
        ci = result.get("customerInsight", {})
        campaigns = result.get("campaigns", [])

        print(f"\n  Customer Insight:")
        print(f"    Segment: {ci.get('ageSegment', '?')} | Churn: {ci.get('churnSegment', '?')} | "
              f"Value: {ci.get('valueSegment', '?')} | Loyalty: {ci.get('loyaltyTier', '?')}")
        print(f"    Affinity: {ci.get('affinityCategory', '?')} ({ci.get('affinityType', '?')})")

        print(f"\n  Kampanyalar ({len(campaigns)} adet):")
        for i, c in enumerate(campaigns, 1):
            print(f"    {i}. {c.get('campaignName', '?')}")
            print(f"       Hedef: {c.get('targetCustomerSegment', '?')} → {c.get('targetProductSegment', '?')[:50]}")
            timing = c.get("timing", {})
            print(f"       Tarih: {timing.get('startDate', '?')} - {timing.get('endDate', '?')}"
                  f"{' (' + timing.get('specialEvent', '') + ')' if timing.get('specialEvent') else ''}")
            ds = c.get("discountSuggestion", {})
            print(f"       İndirim: {ds.get('description', '?')}")

        if summary.get("warnings"):
            print(f"\n  Uyarılar:")
            for w in summary["warnings"]:
                print(f"    ⚠ {w}")

        print()

    # Full JSON'ı da dosyaya yaz
    if not run_all and len(customers_to_test) == 1:
        output_file = os.path.join(os.path.dirname(__file__), "test_orchestrator_output.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"  Full JSON → {output_file}")


if __name__ == "__main__":
    main()
