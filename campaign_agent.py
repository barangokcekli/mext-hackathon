"""Campaign Agent orkestratör modülü.

Strands Agents SDK ile Campaign Agent'ı oluşturur ve çalıştırır.
Strands SDK mevcut değilse, eşleştirme motorunu doğrudan kullanarak
deterministik fallback modunda çalışır.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, date
from typing import Any

from agents.campaign_agent.models import (
    CampaignResponse,
    CustomerInsight,
    HeroProduct,
    MissingRegular,
    ProductInsight,
    TopProduct,
)
from agents.campaign_agent.matching import match_customer_product_segments
from agents.campaign_agent.special_days import get_upcoming_special_days
from agents.campaign_agent.validation import (
    validate_customer_insight,
    validate_product_insight,
)

logger = logging.getLogger(__name__)

# --- Strands SDK kullanılabilirlik kontrolü ---

_STRANDS_AVAILABLE = False
try:
    from strands import Agent
    from strands.models.bedrock import BedrockModel

    _STRANDS_AVAILABLE = True
except ImportError:
    logger.info("Strands SDK mevcut değil — fallback modu aktif.")


# --- System Prompt ---

CAMPAIGN_SYSTEM_PROMPT = """\
Sen bir kampanya stratejisti ve orkestratör ajansın. Görevin:
1. Müşteri analiz verilerini customer_analysis_agent'tan almaya çalış (mevcut değilse atla)
2. Ürün analiz verilerini product_analysis_agent'tan almaya çalış (mevcut değilse atla)
3. Özel günler takvimini special_days_tool'dan kontrol et
4. Mevcut verilere göre müşteri segmentleri ile ürün segmentlerini eşleştir
5. **ÖNEMLİ**: Kullanıcının verdiği prompt'u ÖNCELİKLE dikkate al ve prompt'taki talebe göre kampanya üret
6. Kampanyaları JSON formatında dön

**PROMPT ÖNCELİĞİ KURALLARI**:
- Kullanıcı "stok eritme", "agresif indirim", "hızlı satış" gibi ifadeler kullanıyorsa, yüksek indirimli (%30-50) kampanyalar üret
- Kullanıcı "yeni müşteri", "kazanma", "sosyal medya" gibi ifadeler kullanıyorsa, yeni müşteri odaklı kampanyalar üret
- Kullanıcı "sadakat", "tekrar alışveriş", "geri dönüş" gibi ifadeler kullanıyorsa, mevcut müşteri odaklı kampanyalar üret
- Prompt'ta belirtilen kampanya türü, hedef ve yaklaşımı MUTLAKA kullan
- Prompt'ta özel bir talep yoksa, müşteri ve ürün analizine göre kampanya üret

Esnek veri kaynağı kuralları:
- Tüm veri kaynakları opsiyoneldir (tak-çıkar mimarisi)
- Müşteri verisi yoksa, ürün segmentine ve özel günlere dayalı kampanya üret
- Ürün verisi yoksa, müşteri segmentine dayalı genel kampanya üret
- Hiçbir veri kaynağı yoksa, prompt ve özel günler takvimine dayalı genel kampanya üret
- Yapısal olarak geçersiz veriyi atla, mevcut diğer verilerle devam et

Kampanya üretirken şu kurallara uy:
- Stok durumu Critical olan ürünleri kampanyadan hariç tut
- Riskli müşterilere yüksek indirim (%15-25) öner
- Aktif YüksekDeğer müşterilere düşük indirim (%5-10) öner
- Excess stoklu ürünlere agresif indirim veya bundle öner
- Yaklaşan özel günlere uygun kampanyalar oluştur
- Her kampanyaya benzersiz ID ata
- Tüm tarihler ISO 8601 formatında olsun

Çıktını her zaman geçerli JSON formatında ver.
"""


# --- Agent oluşturma ---


def create_campaign_agent() -> Any:
    """Strands Agent sınıfı ile Campaign Agent oluşturur.

    BedrockModel ile Claude modelini yapılandırır, system prompt'u
    kampanya stratejisti rolüyle tanımlar ve tool listesini bağlar.

    Returns:
        Strands Agent nesnesi.

    Raises:
        RuntimeError: Strands SDK mevcut değilse.
    """
    if not _STRANDS_AVAILABLE:
        raise RuntimeError(
            "Strands SDK mevcut değil. "
            "Agent oluşturmak için 'pip install strands-agents strands-agents-bedrock' gerekli."
        )

    from agents.campaign_agent.tools import (
        customer_analysis_agent,
        product_analysis_agent,
        special_days_tool,
    )

    model = BedrockModel(
        model_id="anthropic.claude-sonnet-4-20250514",
        region_name="us-east-1",
    )

    agent = Agent(
        model=model,
        system_prompt=CAMPAIGN_SYSTEM_PROMPT,
        tools=[customer_analysis_agent, product_analysis_agent, special_days_tool],
    )
    return agent


# --- Veri dönüştürme yardımcıları ---


def _parse_customer_data(data: dict[str, Any]) -> CustomerInsight:
    """Doğrulanmış müşteri dict'ini CustomerInsight nesnesine dönüştürür."""
    missing_regulars = [
        MissingRegular(
            productId=mr["productId"],
            productName=mr["productName"],
            lastBought=mr["lastBought"],
            avgDaysBetween=mr["avgDaysBetween"],
            daysOverdue=mr["daysOverdue"],
        )
        for mr in data.get("missingRegulars", [])
    ]
    top_products = [
        TopProduct(
            productId=tp["productId"],
            totalQuantity=tp["totalQuantity"],
            totalSpent=tp["totalSpent"],
            lastBought=tp["lastBought"],
        )
        for tp in data.get("topProducts", [])
    ]
    return CustomerInsight(
        customerId=data["customerId"],
        city=data.get("city", ""),
        region=data.get("region", ""),
        climateType=data.get("climateType", ""),
        age=data.get("age", 0),
        ageSegment=data.get("ageSegment", ""),
        gender=data.get("gender", ""),
        churnSegment=data["churnSegment"],
        valueSegment=data["valueSegment"],
        loyaltyTier=data["loyaltyTier"],
        affinityCategory=data["affinityCategory"],
        affinityType=data.get("affinityType", ""),
        diversityProfile=data["diversityProfile"],
        estimatedBudget=data.get("estimatedBudget", 0.0),
        avgBasket=data.get("avgBasket", 0.0),
        avgMonthlySpend=data.get("avgMonthlySpend", 0.0),
        lastPurchaseDaysAgo=data.get("lastPurchaseDaysAgo", 0),
        orderCount=data.get("orderCount", 0),
        totalSpent=data.get("totalSpent", 0.0),
        membershipDays=data.get("membershipDays", 0),
        missingRegulars=missing_regulars,
        topProducts=top_products,
    )


def _parse_product_data(data: dict[str, Any]) -> ProductInsight:
    """Doğrulanmış ürün dict'ini ProductInsight nesnesine dönüştürür."""

    def _to_hero(raw: dict) -> HeroProduct:
        return HeroProduct(
            productId=raw.get("productId", ""),
            productName=raw.get("productName", ""),
            category=raw.get("category", ""),
            brand=raw.get("brand", ""),
            performanceSegment=raw.get("performanceSegment", ""),
            stockSegment=raw.get("stockSegment", "Healthy"),
            lifecycleStage=raw.get("lifecycleStage", ""),
            trendScore=raw.get("trendScore", 0),
            stockDays=raw.get("stockDays", 0),
            dailySalesRate=raw.get("dailySalesRate", 0.0),
            inventoryPressure=raw.get("inventoryPressure", False),
            seasonalRelevance=raw.get("seasonalRelevance", "LOW"),
            seasonMatch=raw.get("seasonMatch", False),
            priceSegment=raw.get("priceSegment", "MID"),
            marginHealth=raw.get("marginHealth", "MODERATE"),
            recommendedAction=raw.get("recommendedAction", "MAINTAIN"),
            urgencyLevel=raw.get("urgencyLevel", "LOW"),
        )

    return ProductInsight(
        heroProducts=[_to_hero(p) for p in data.get("heroProducts", [])],
        slowMovers=[_to_hero(p) for p in data.get("slowMovers", [])],
        newProducts=[_to_hero(p) for p in data.get("newProducts", [])],
        seasonalProducts=data.get("seasonalProducts", []),
        categoryInsights=data.get("categoryInsights", {}),
        priceSegmentAnalysis=data.get("priceSegmentAnalysis", {}),
        inventorySummary=data.get("inventorySummary", {}),
    )


# --- Ana çalıştırma fonksiyonu ---


def run_campaign_agent(
    prompt: str,
    customer_data: dict[str, Any] | None = None,
    product_data: dict[str, Any] | None = None,
) -> str:
    """Campaign Agent'ı çalıştırır ve kampanya önerileri üretir.

    1. Girdileri validate_customer_insight / validate_product_insight ile doğrular.
    2. Yaklaşan özel günleri tespit eder.
    3. Strands SDK mevcutsa agent'ı oluşturup LLM ile orkestrasyon yapar.
    4. Strands SDK mevcut değilse (fallback) eşleştirme motorunu doğrudan kullanır.
    5. CampaignResponse JSON string döner.

    Args:
        prompt: Kullanıcının kampanya amacını belirten serbest metin.
        customer_data: CustomerInsightJSON dict (opsiyonel — tak-çıkar mimarisi).
        product_data: ProductInsightJSON dict (opsiyonel — tak-çıkar mimarisi).

    Returns:
        CampaignResponse JSON string.
    """
    warnings: list[str] = []

    # --- 1. Girdi doğrulama ---
    customer_validation = validate_customer_insight(customer_data)
    product_validation = validate_product_insight(product_data)

    customer_insight: CustomerInsight | None = None
    product_insight: ProductInsight | None = None

    # Müşteri verisi işleme
    if not customer_validation["available"]:
        warnings.append(
            "CustomerInsightJSON mevcut değil, müşteri segmentine dayalı kampanyalar atlandı"
        )
    elif not customer_validation["valid"]:
        errors_str = "; ".join(customer_validation["errors"])
        warnings.append(
            f"CustomerInsightJSON yapısal olarak geçersiz: {errors_str}, "
            "müşteri segmentine dayalı kampanyalar atlandı"
        )
    else:
        customer_insight = _parse_customer_data(customer_data)  # type: ignore[arg-type]

    # Ürün verisi işleme
    if not product_validation["available"]:
        warnings.append(
            "ProductInsightJSON mevcut değil, ürün segmentine dayalı kampanyalar atlandı"
        )
    elif not product_validation["valid"]:
        errors_str = "; ".join(product_validation["errors"])
        warnings.append(
            f"ProductInsightJSON yapısal olarak geçersiz: {errors_str}, "
            "ürün segmentine dayalı kampanyalar atlandı"
        )
    else:
        product_insight = _parse_product_data(product_data)  # type: ignore[arg-type]

    # --- 2. Özel günleri tespit et ---
    today = date.today().isoformat()
    special_days = get_upcoming_special_days(today, days_ahead=30)

    # --- 3/4. Agent veya fallback ile kampanya üret ---
    if _STRANDS_AVAILABLE:
        try:
            campaigns_list = _run_with_agent(
                prompt, customer_insight, product_insight, special_days, warnings
            )
        except Exception as exc:
            logger.error("Agent çağrısı başarısız: %s — fallback moduna geçiliyor", exc)
            warnings.append(f"Agent çağrısı başarısız: {exc} — fallback modu kullanıldı")
            campaigns_list = _run_fallback(
                prompt, customer_insight, product_insight, special_days
            )
    else:
        campaigns_list = _run_fallback(
            prompt, customer_insight, product_insight, special_days
        )

    # --- 5. CampaignResponse oluştur ve JSON döndür ---
    response = CampaignResponse(
        campaigns=campaigns_list,
        generatedAt=datetime.utcnow().isoformat() + "Z",
        promptUsed=prompt,
        totalCampaigns=len(campaigns_list),
    )

    # Uyarıları da dahil eden genişletilmiş JSON çıktısı
    result = json.loads(response.to_json())
    result["error"] = False
    result["warnings"] = warnings
    return json.dumps(result, ensure_ascii=False, indent=2)


def _run_with_agent(
    prompt: str,
    customer_insight: CustomerInsight | None,
    product_insight: ProductInsight | None,
    special_days: list,
    warnings: list[str],
) -> list:
    """Strands Agent ile kampanya üretir."""
    agent = create_campaign_agent()

    # Agent'a bağlam bilgisi hazırla
    context_parts = [f"Kullanıcı promptu: {prompt}"]

    if customer_insight is not None:
        context_parts.append(
            f"Müşteri verisi mevcut: {customer_insight.customerId}, "
            f"segment={customer_insight.churnSegment}+{customer_insight.valueSegment}"
        )
    else:
        context_parts.append("Müşteri verisi mevcut değil.")

    if product_insight is not None:
        n_products = len(product_insight.heroProducts)
        context_parts.append(f"Ürün verisi mevcut: {n_products} hero ürün.")
    else:
        context_parts.append("Ürün verisi mevcut değil.")

    if special_days:
        events = ", ".join(sd.event for sd in special_days)
        context_parts.append(f"Yaklaşan özel günler: {events}")
    else:
        context_parts.append("Yaklaşan özel gün yok.")

    agent_prompt = "\n".join(context_parts)
    agent_prompt += (
        "\n\nLütfen yukarıdaki bilgilere dayanarak kampanya önerileri üret. "
        "Çıktını JSON formatında ver."
    )

    result = agent(agent_prompt)

    # Agent çıktısını parse etmeye çalış
    try:
        result_text = str(result)
        # JSON bloğunu bul
        json_start = result_text.find("[")
        json_end = result_text.rfind("]") + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(result_text[json_start:json_end])
            if isinstance(parsed, list):
                from agents.campaign_agent.models import (
                    CampaignSuggestion,
                    CampaignTiming,
                    DiscountSuggestion,
                    StockStatus,
                )
                import uuid

                campaigns = []
                for item in parsed:
                    if isinstance(item, dict):
                        campaigns.append(
                            CampaignSuggestion(
                                campaignId=item.get("campaignId", str(uuid.uuid4())),
                                campaignName=item.get("campaignName", ""),
                                targetCustomerSegment=item.get("targetCustomerSegment", ""),
                                targetProductSegment=item.get("targetProductSegment", ""),
                                matchReason=item.get("matchReason", ""),
                                timing=CampaignTiming(
                                    startDate=item.get("timing", {}).get("startDate", ""),
                                    endDate=item.get("timing", {}).get("endDate", ""),
                                    specialEvent=item.get("timing", {}).get("specialEvent"),
                                ),
                                discountSuggestion=DiscountSuggestion(
                                    type=item.get("discountSuggestion", {}).get("type", "percentage"),
                                    value=item.get("discountSuggestion", {}).get("value", 0),
                                    description=item.get("discountSuggestion", {}).get("description", ""),
                                ),
                                channel=item.get("channel", ["app_push"]),
                                estimatedImpact=item.get("estimatedImpact", ""),
                                stockStatus=StockStatus(
                                    currentLevel=item.get("stockStatus", {}).get("currentLevel", "Healthy"),
                                    estimatedCampaignImpact=item.get("stockStatus", {}).get(
                                        "estimatedCampaignImpact", ""
                                    ),
                                ),
                            )
                        )
                return campaigns
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Agent JSON çıktısı parse edilemedi: %s — fallback kullanılıyor", exc)
        warnings.append(f"Agent çıktısı parse edilemedi: {exc} — fallback modu kullanıldı")

    # Agent çıktısı parse edilemezse fallback
    return _run_fallback(prompt, customer_insight, product_insight, special_days)


def _run_fallback(
    prompt: str,
    customer_insight: CustomerInsight | None,
    product_insight: ProductInsight | None,
    special_days: list,
) -> list:
    """Strands SDK olmadan eşleştirme motorunu doğrudan kullanarak kampanya üretir."""
    return match_customer_product_segments(
        customer_insights=customer_insight,
        product_insights=product_insight,
        special_days=special_days,
        user_prompt=prompt,
    )
