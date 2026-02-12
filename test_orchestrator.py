"""
Orchestrator Agent test script — customers-100.json + products_2.json ile.

Kullanım:
    python test_orchestrator.py                    # Deterministik mod, C-2001
    python test_orchestrator.py --customer C-2005  # Belirli müşteri
    python test_orchestrator.py --all              # Tüm müşteriler (100)
    python test_orchestrator.py --llm              # LLM-based orchestrator
    python test_orchestrator.py --limit 5          # İlk 5 müşteri
"""

import json
import sys
import os
import time

# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)

CUSTOMERS_FILE = os.path.join(BASE_DIR, "customer-segment-agent", "mock-data", "farmasi", "customers-100.json")
PRODUCTS_FILE = os.path.join(BASE_DIR, "product-agent", "data", "products_2.json")
REGIONS_FILE = os.path.join(BASE_DIR, "customer-segment-agent", "mock-data", "regions.json")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
    ALL_CUSTOMERS = json.load(f)

with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    PRODUCT_DATA = json.load(f)

with open(REGIONS_FILE, "r", encoding="utf-8") as f:
    REGIONS_DATA = json.load(f)

REGION_MAP = {r["name"]: r for r in REGIONS_DATA["regions"]}


def build_customer_payload(customer: dict) -> dict:
    """customers-100.json formatını customer segment agent payload'ına dönüştürür."""
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
    """products_2.json'dan product agent payload'ı oluşturur (subset)."""
    products = PRODUCT_DATA["products"][:max_products]
    orders = PRODUCT_DATA.get("orderHistory", [])[:5]

    return {
        "tenantId": PRODUCT_DATA["tenantId"],
        "products": products,
        "orderHistory": orders,
        "currentMonth": PRODUCT_DATA.get("currentMonth", 2),
        "climateData": PRODUCT_DATA.get("climateData", {}),
    }


def print_result(customer: dict, result: dict):
    """Sonucu güzel formatta yazdırır."""
    summary = result.get("orchestrationSummary", {})
    ci = result.get("customerInsight", {})
    campaigns = result.get("campaigns", [])

    print(f"\n  Customer Insight:")
    if isinstance(ci, dict) and ci:
        print(f"    Segment: {ci.get('ageSegment', '?')} | Churn: {ci.get('churnSegment', '?')} | "
              f"Value: {ci.get('valueSegment', '?')} | Loyalty: {ci.get('loyaltyTier', '?')}")
        print(f"    Affinity: {ci.get('affinityCategory', '?')} ({ci.get('affinityType', '?')})")
    else:
        print(f"    Raw: {str(ci)[:200]}")

    print(f"\n  Kampanyalar ({len(campaigns)} adet):")
    for i, c in enumerate(campaigns, 1):
        if isinstance(c, dict):
            print(f"    {i}. {c.get('campaignName', c.get('name', '?'))}")
            target = c.get('targetCustomerSegment', c.get('target', '?'))
            product_target = str(c.get('targetProductSegment', c.get('products', '')))[:60]
            print(f"       Hedef: {target} → {product_target}")
            timing = c.get("timing", {})
            if timing:
                print(f"       Tarih: {timing.get('startDate', '?')} - {timing.get('endDate', '?')}"
                      f"{' (' + timing.get('specialEvent', '') + ')' if timing.get('specialEvent') else ''}")
            ds = c.get("discountSuggestion", c.get("discount", {}))
            if ds:
                print(f"       İndirim: {ds.get('description', ds) if isinstance(ds, dict) else ds}")
        else:
            print(f"    {i}. {str(c)[:100]}")

    if summary.get("warnings"):
        print(f"\n  Uyarılar:")
        for w in summary["warnings"]:
            print(f"    ⚠ {w}")


def main():
    from orchestrator_agent import orchestrate_campaign

    # Parse args
    customer_id = "C-2001"
    run_all = "--all" in sys.argv
    use_llm = "--llm" in sys.argv
    limit = None

    for i, arg in enumerate(sys.argv):
        if arg == "--customer" and i + 1 < len(sys.argv):
            customer_id = sys.argv[i + 1]
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    # Product payload — 30 ürün subset
    product_payload = build_product_payload(max_products=30)

    # Müşteri seçimi
    if run_all:
        customers_to_test = ALL_CUSTOMERS[:limit] if limit else ALL_CUSTOMERS
    elif limit:
        customers_to_test = ALL_CUSTOMERS[:limit]
    else:
        customers_to_test = [c for c in ALL_CUSTOMERS if c["customerId"] == customer_id]
        if not customers_to_test:
            print(f"Müşteri bulunamadı: {customer_id}")
            print(f"İlk 10 müşteri: {[c['customerId'] for c in ALL_CUSTOMERS[:10]]}")
            return

    mode = "LLM" if use_llm else "Deterministik"
    print(f"\n{'='*70}")
    print(f"  Orchestrator Test — {mode} mod")
    print(f"  Müşteri sayısı: {len(customers_to_test)} | Ürün sayısı: {len(product_payload['products'])}")
    print(f"{'='*70}")

    all_results = []
    total_start = time.time()

    for idx, customer in enumerate(customers_to_test, 1):
        customer_payload = build_customer_payload(customer)
        prompt = "Kış sezonu için bu müşteriye özel kişiselleştirilmiş kampanya önerileri oluştur"

        print(f"\n{'─'*70}")
        print(f"  [{idx}/{len(customers_to_test)}] {customer['customerId']} | "
              f"{customer['city']} | Yaş: {customer['age']} | "
              f"Cinsiyet: {customer['gender']} | "
              f"Toplam sipariş: {customer.get('totalOrders', '?')} | "
              f"LTV: {customer.get('totalLifetimeValue', '?')} TL")
        print(f"  Ürün geçmişi: {len(customer['productHistory'])} ürün | "
              f"Segment: {customer.get('valueSegment', '?')} | "
              f"Churn: {customer.get('churnRisk', '?')}")
        print(f"{'─'*70}")

        start = time.time()
        result = orchestrate_campaign(
            prompt=prompt,
            customer_data=customer_payload,
            product_data=product_payload,
            use_llm=use_llm,
        )
        elapsed = time.time() - start

        print_result(customer, result)
        print(f"\n  ⏱ Süre: {elapsed:.1f}s")

        all_results.append({
            "customerId": customer["customerId"],
            "result": result,
            "elapsed": round(elapsed, 1),
        })

    total_elapsed = time.time() - total_start

    # Özet
    print(f"\n{'='*70}")
    print(f"  TOPLAM: {len(all_results)} müşteri | {total_elapsed:.1f}s | "
          f"Ort: {total_elapsed/len(all_results):.1f}s/müşteri")
    total_campaigns = sum(len(r["result"].get("campaigns", [])) for r in all_results)
    print(f"  Toplam kampanya: {total_campaigns}")
    print(f"{'='*70}")

    # JSON çıktı
    output_file = os.path.join(BASE_DIR, "test_orchestrator_output.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n  Full JSON → {output_file}")


if __name__ == "__main__":
    main()
