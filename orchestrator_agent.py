"""
Orchestrator Agent - Multi-Agent Campaign Generation

Strands SDK "Agents as Tools" pattern kullanarak AgentCore Runtime'a
deploy edilmiş 3 agent'ı koordine eder:

1. Customer Segment Agent → Müşteri segmentasyonu
2. Product Analysis Agent → Ürün analizi
3. Campaign Agent → Kampanya üretimi

Flow:
  User Input (customer_data + product_data + prompt)
       │
       ├──► Customer Segment Agent (customer_data)
       │         │
       │         ▼ customer_insight
       │
       ├──► Product Analysis Agent (product_data)
       │         │
       │         ▼ product_insight
       │
       └──► Campaign Agent (customer_insight + product_insight + prompt)
                  │
                  ▼ campaign_result
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import boto3
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# ---------------------------------------------------------------------------
# Agent ARN Configuration (environment variables ile override edilebilir)
# ---------------------------------------------------------------------------
CUSTOMER_SEGMENT_AGENT_ARN = os.environ.get(
    "CUSTOMER_SEGMENT_AGENT_ARN",
    "arn:aws:bedrock-agentcore:us-west-2:472634336236:runtime/customer_segment_agent-AF1ggg7Wx7",
)
PRODUCT_ANALYSIS_AGENT_ARN = os.environ.get(
    "PRODUCT_ANALYSIS_AGENT_ARN",
    "arn:aws:bedrock-agentcore:us-west-2:472634336236:runtime/product_analysis_agent_kiro-cDTDVBBnei",
)
CAMPAIGN_AGENT_ARN = os.environ.get(
    "CAMPAIGN_AGENT_ARN",
    "arn:aws:bedrock-agentcore:us-west-2:472634336236:runtime/campaignAgentV2-yYLVYD40Dp",
)

AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")

# ---------------------------------------------------------------------------
# AgentCore Runtime client
# ---------------------------------------------------------------------------
agentcore_client = boto3.client("bedrock-agentcore", region_name=AWS_REGION)


def invoke_agentcore_runtime(agent_arn: str, payload: dict, session_id: str | None = None) -> dict:
    """
    AgentCore Runtime üzerinde deploy edilmiş bir agent'ı invoke eder.

    Args:
        agent_arn: Agent'ın AgentCore Runtime ARN'ı
        payload: Agent'a gönderilecek JSON payload
        session_id: Opsiyonel session ID (conversation context için)

    Returns:
        Agent'ın döndürdüğü parsed JSON response
    """
    invoke_params: Dict[str, Any] = {
        "agentRuntimeArn": agent_arn,
        "payload": json.dumps(payload).encode("utf-8"),
    }
    if session_id:
        invoke_params["runtimeSessionId"] = session_id

    logger.info("Invoking AgentCore Runtime: %s", agent_arn.split("/")[-1])

    response = agentcore_client.invoke_agent_runtime(**invoke_params)

    # Response body'yi oku — StreamingBody döner
    response_body = response.get("response", b"")

    if hasattr(response_body, "read"):
        raw = response_body.read()
    else:
        raw = response_body if isinstance(response_body, bytes) else str(response_body).encode("utf-8")

    text = raw.decode("utf-8").strip()

    # JSON parse et
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # JSON bloğu bulmaya çalış (agent bazen text + JSON döner)
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            try:
                return json.loads(text[json_start:json_end])
            except json.JSONDecodeError:
                pass
        # Array olabilir
        json_start = text.find("[")
        json_end = text.rfind("]") + 1
        if json_start >= 0 and json_end > json_start:
            try:
                return {"data": json.loads(text[json_start:json_end])}
            except json.JSONDecodeError:
                pass
        logger.warning("Agent response JSON olarak parse edilemedi, raw text dönülüyor")
        return {"raw_response": text}


# ---------------------------------------------------------------------------
# Tool Definitions — Her agent bir @tool olarak sarmalanıyor
# ---------------------------------------------------------------------------

@tool
def analyze_customer_segment(customer_data: str) -> str:
    """
    Müşteri verisini analiz ederek segmentasyon bilgisi üretir.
    Customer Segment Agent'ı AgentCore Runtime üzerinden çağırır.

    Args:
        customer_data: JSON string formatında müşteri verisi.
            Beklenen format:
            {
                "customerId": "C-1001",
                "city": "Istanbul",
                "customer": { "age": 32, "gender": "F", "registeredAt": "...", "productHistory": [...] },
                "region": { "name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "SKINCARE" }
            }

    Returns:
        JSON string formatında müşteri segmentasyon sonucu
    """
    try:
        data = json.loads(customer_data) if isinstance(customer_data, str) else customer_data
        payload = {"customerData": data}

        result = invoke_agentcore_runtime(CUSTOMER_SEGMENT_AGENT_ARN, payload)
        logger.info("Customer segment analysis tamamlandı: %s", data.get("customerId", "N/A"))
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Customer segment analysis hatası: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@tool
def analyze_products(product_data: str) -> str:
    """
    Ürün verisini analiz ederek ürün segmentasyonu ve öneriler üretir.
    Product Analysis Agent'ı AgentCore Runtime üzerinden çağırır.

    Args:
        product_data: JSON string formatında ürün verisi.
            Beklenen format:
            {
                "tenantId": "farmasi",
                "products": [...],
                "orderHistory": [...],
                "currentMonth": 2,
                "climateData": { "Istanbul": { "avgTempC": 8, ... } }
            }

    Returns:
        JSON string formatında ürün analiz sonucu (heroProducts, slowMovers, vb.)
    """
    try:
        data = json.loads(product_data) if isinstance(product_data, str) else product_data

        result = invoke_agentcore_runtime(PRODUCT_ANALYSIS_AGENT_ARN, data)
        logger.info("Product analysis tamamlandı: %d ürün", len(data.get("products", [])))
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Product analysis hatası: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


@tool
def generate_campaign(campaign_input: str) -> str:
    """
    Müşteri segmentasyonu ve ürün analizi sonuçlarını kullanarak kampanya üretir.
    Campaign Agent'ı AgentCore Runtime üzerinden çağırır.

    Args:
        campaign_input: JSON string formatında kampanya girdisi.
            Beklenen format:
            {
                "prompt": "Yaz kampanyası oluştur",
                "customerData": { ... customer segment analysis sonucu ... },
                "productData": { ... product analysis sonucu ... }
            }

    Returns:
        JSON string formatında kampanya önerileri
    """
    try:
        data = json.loads(campaign_input) if isinstance(campaign_input, str) else campaign_input

        if CAMPAIGN_AGENT_ARN:
            result = invoke_agentcore_runtime(CAMPAIGN_AGENT_ARN, data)
        else:
            # Campaign agent henüz deploy edilmediyse local fallback
            logger.info("Campaign Agent ARN tanımlı değil, local fallback kullanılıyor")
            from campaign_agent import run_campaign_agent
            result_str = run_campaign_agent(
                prompt=data.get("prompt", ""),
                customer_data=data.get("customerData"),
                product_data=data.get("productData"),
            )
            result = json.loads(result_str)

        logger.info("Campaign generation tamamlandı")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Campaign generation hatası: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})



# ---------------------------------------------------------------------------
# Orchestrator Agent — System Prompt & Agent oluşturma
# ---------------------------------------------------------------------------

ORCHESTRATOR_SYSTEM_PROMPT = """\
Sen bir kampanya orkestratör ajanısın. Görevin kullanıcıdan gelen müşteri ve ürün
verilerini alıp, doğru sırayla alt ajanlara göndererek kişiselleştirilmiş kampanya
önerileri üretmektir.

## İş Akışı

1. Kullanıcıdan gelen input'u analiz et. Input şunları içerebilir:
   - customerData: Müşteri bilgileri (demographics, purchase history)
   - productData: Ürün bilgileri (products, orderHistory, climateData)
   - prompt: Kampanya amacını belirten serbest metin

2. customerData mevcutsa → analyze_customer_segment tool'unu çağır
   - Müşteri segmentasyonu sonucunu al (churnSegment, valueSegment, loyaltyTier vb.)

3. productData mevcutsa → analyze_products tool'unu çağır
   - Ürün analizi sonucunu al (heroProducts, slowMovers, seasonalProducts vb.)

4. Her iki analiz tamamlandıktan sonra → generate_campaign tool'unu çağır
   - customer segment sonucu + product analysis sonucu + kullanıcı prompt'unu birleştir
   - Kampanya önerilerini üret

## Kurallar

- Müşteri ve ürün analizlerini PARALEL olarak başlatabilirsin (birbirinden bağımsızlar)
- Bir veri kaynağı yoksa (customerData veya productData null/boş), o analizi atla
- Her iki analiz de yoksa, sadece prompt ve genel bilgiye dayalı kampanya üret
- Hata durumunda kullanıcıya açıklayıcı mesaj ver
- Tüm çıktıları JSON formatında döndür
- Türkçe açıklamalar kullan

## Çıktı Formatı

Sonucu şu yapıda döndür:
{
  "customerInsight": { ... },  // Customer segment sonucu (varsa)
  "productInsight": { ... },   // Product analysis sonucu (varsa)
  "campaigns": [ ... ],        // Üretilen kampanyalar
  "orchestrationSummary": {
    "customerAnalyzed": true/false,
    "productAnalyzed": true/false,
    "campaignCount": N,
    "warnings": [...]
  }
}
"""


def create_orchestrator_agent() -> Agent:
    """Orchestrator Agent'ı oluşturur."""
    model = BedrockModel(
        model_id="global.anthropic.claude-opus-4-5-20251101-v1:0",
        region_name=AWS_REGION,
    )

    orchestrator = Agent(
        model=model,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=[analyze_customer_segment, analyze_products, generate_campaign],
    )
    return orchestrator


# ---------------------------------------------------------------------------
# Programmatic orchestration (LLM olmadan deterministik akış)
# ---------------------------------------------------------------------------

def orchestrate_campaign(
    prompt: str,
    customer_data: dict | None = None,
    product_data: dict | None = None,
    use_llm: bool = True,
) -> dict:
    """
    Kampanya üretimi için tam orkestrasyon akışını çalıştırır.

    Args:
        prompt: Kampanya amacını belirten serbest metin
        customer_data: Müşteri verisi (opsiyonel)
        product_data: Ürün verisi (opsiyonel)
        use_llm: True ise LLM-based orchestrator kullanır, False ise deterministik akış

    Returns:
        Orkestrasyon sonucu dict
    """
    if use_llm:
        return _orchestrate_with_llm(prompt, customer_data, product_data)
    else:
        return _orchestrate_deterministic(prompt, customer_data, product_data)


def _orchestrate_with_llm(
    prompt: str,
    customer_data: dict | None,
    product_data: dict | None,
) -> dict:
    """LLM-based orchestrator ile kampanya üretir."""
    agent = create_orchestrator_agent()

    # Agent'a gönderilecek mesajı hazırla
    message_parts = [f"Kampanya oluştur: {prompt}"]

    if customer_data:
        message_parts.append(f"\nMüşteri verisi:\n{json.dumps(customer_data, ensure_ascii=False)}")
    else:
        message_parts.append("\nMüşteri verisi mevcut değil.")

    if product_data:
        message_parts.append(f"\nÜrün verisi:\n{json.dumps(product_data, ensure_ascii=False)}")
    else:
        message_parts.append("\nÜrün verisi mevcut değil.")

    agent_message = "\n".join(message_parts)
    result = agent(agent_message)

    # Agent çıktısını parse et
    result_text = str(result)
    try:
        json_start = result_text.find("{")
        json_end = result_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(result_text[json_start:json_end])
    except json.JSONDecodeError:
        pass

    return {"raw_response": result_text}


def _orchestrate_deterministic(
    prompt: str,
    customer_data: dict | None,
    product_data: dict | None,
) -> dict:
    """Deterministik akış ile kampanya üretir (LLM kullanmadan)."""
    warnings = []
    customer_insight = None
    product_insight = None

    # Step 1: Customer segment analysis
    if customer_data:
        try:
            logger.info("Step 1: Customer segment analysis başlatılıyor...")
            raw = invoke_agentcore_runtime(CUSTOMER_SEGMENT_AGENT_ARN, {"customerData": customer_data})
            # Customer agent "analysis" key altında veya "result" key altında dönebilir
            customer_insight = raw.get("analysis", raw.get("result", raw))
            logger.info("Customer segment analysis tamamlandı")
        except Exception as e:
            warnings.append(f"Customer segment analysis hatası: {str(e)}")
            logger.error("Customer segment analysis hatası: %s", e)
    else:
        warnings.append("Müşteri verisi sağlanmadı, müşteri analizi atlandı")

    # Step 2: Product analysis
    if product_data:
        try:
            logger.info("Step 2: Product analysis başlatılıyor...")
            product_insight = invoke_agentcore_runtime(PRODUCT_ANALYSIS_AGENT_ARN, product_data)
            logger.info("Product analysis tamamlandı")
        except Exception as e:
            warnings.append(f"Product analysis hatası: {str(e)}")
            logger.error("Product analysis hatası: %s", e)
    else:
        warnings.append("Ürün verisi sağlanmadı, ürün analizi atlandı")

    # Step 3: Campaign generation
    logger.info("Step 3: Campaign generation başlatılıyor...")
    campaign_payload = {
        "prompt": prompt,
        "customerData": customer_insight,
        "productData": product_insight,
    }

    try:
        if CAMPAIGN_AGENT_ARN:
            campaign_result = invoke_agentcore_runtime(CAMPAIGN_AGENT_ARN, campaign_payload)
        else:
            from campaign_agent import run_campaign_agent
            campaign_str = run_campaign_agent(
                prompt=prompt,
                customer_data=customer_insight,
                product_data=product_insight,
            )
            campaign_result = json.loads(campaign_str)
        logger.info("Campaign generation tamamlandı")
    except Exception as e:
        warnings.append(f"Campaign generation hatası: {str(e)}")
        logger.error("Campaign generation hatası: %s", e)
        campaign_result = {"campaigns": [], "error": str(e)}

    campaigns = campaign_result.get("campaigns", [])

    return {
        "customerInsight": customer_insight,
        "productInsight": product_insight,
        "campaigns": campaigns,
        "orchestrationSummary": {
            "customerAnalyzed": customer_insight is not None,
            "productAnalyzed": product_insight is not None,
            "campaignCount": len(campaigns),
            "warnings": warnings,
        },
    }


# ---------------------------------------------------------------------------
# AgentCore Runtime Entrypoint
# ---------------------------------------------------------------------------

@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrator Agent'ın AgentCore Runtime entrypoint'i.

    Payload formatı:
    {
        "prompt": "Yaz kampanyası oluştur",
        "customerData": { ... },
        "productData": { ... },
        "useLLM": true/false  (opsiyonel, default: true)
    }
    """
    logger.info("=== Orchestrator Agent invocation started ===")

    try:
        # Handle Sandbox format: {"prompt": "...json string..."}
        if isinstance(payload, dict) and "prompt" in payload and len(payload) == 1:
            prompt_value = payload["prompt"]
            if isinstance(prompt_value, str):
                try:
                    parsed = json.loads(prompt_value)
                    if isinstance(parsed, dict) and ("customerData" in parsed or "productData" in parsed):
                        payload = parsed
                except (json.JSONDecodeError, ValueError):
                    pass

        prompt = payload.get("prompt", "Kişiselleştirilmiş kampanya önerileri oluştur")
        customer_data = payload.get("customerData")
        product_data = payload.get("productData")
        use_llm = payload.get("useLLM", True)

        result = orchestrate_campaign(
            prompt=prompt,
            customer_data=customer_data,
            product_data=product_data,
            use_llm=use_llm,
        )

        logger.info(
            "=== Orchestrator completed: %d campaigns generated ===",
            result.get("orchestrationSummary", {}).get("campaignCount", 0),
        )
        return result

    except Exception as e:
        logger.error("Orchestrator hatası: %s", e, exc_info=True)
        return {
            "error": str(e),
            "message": "Orchestrator işlemi başarısız oldu",
            "customerInsight": None,
            "productInsight": None,
            "campaigns": [],
            "orchestrationSummary": {
                "customerAnalyzed": False,
                "productAnalyzed": False,
                "campaignCount": 0,
                "warnings": [str(e)],
            },
        }


if __name__ == "__main__":
    app.run()
