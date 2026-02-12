"""
Orchestrator Wrapper - Strands SDK olmadan orchestrator fonksiyonlarını kullanır
"""

import json
import logging
import os
import boto3
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent ARNs
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
TARGET_ACCOUNT_ID = "472634336236"
CROSS_ACCOUNT_ROLE = os.environ.get(
    "CROSS_ACCOUNT_ROLE",
    f"arn:aws:iam::{TARGET_ACCOUNT_ID}:role/AgentCoreInvokeRole"
)

# Try to assume cross-account role
def get_agentcore_client():
    """Get AgentCore client with cross-account credentials if needed"""
    # Direkt credentials kullan, AssumeRole gereksiz
    logger.info("Using environment credentials for AgentCore")
    return boto3.client("bedrock-agentcore", region_name=AWS_REGION)

agentcore_client = get_agentcore_client()


def invoke_agentcore_runtime(agent_arn: str, payload: dict, session_id: Optional[str] = None) -> dict:
    """
    AgentCore Runtime üzerinde deploy edilmiş bir agent'ı invoke eder.
    """
    invoke_params: Dict[str, Any] = {
        "agentRuntimeArn": agent_arn,
        "payload": json.dumps(payload).encode("utf-8"),
    }
    if session_id:
        invoke_params["runtimeSessionId"] = session_id

    logger.info("Invoking AgentCore Runtime: %s", agent_arn.split("/")[-1])

    response = agentcore_client.invoke_agent_runtime(**invoke_params)

    # Response body'yi oku
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
        # JSON bloğu bulmaya çalış
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


def orchestrate_campaign_deterministic(
    prompt: str,
    customer_data: Optional[dict] = None,
    product_data: Optional[dict] = None,
) -> dict:
    """
    Deterministik akış ile kampanya üretir (AgentCore Runtime kullanarak)
    """
    warnings = []
    customer_insight = None
    product_insight = None

    # Step 1: Customer segment analysis
    if customer_data:
        try:
            logger.info("Step 1: Customer segment analysis başlatılıyor...")
            raw = invoke_agentcore_runtime(CUSTOMER_SEGMENT_AGENT_ARN, {"customerData": customer_data})
            customer_insight = raw.get("analysis", raw.get("result", raw))
            logger.info("✓ Customer segment analysis tamamlandı")
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
            logger.info("✓ Product analysis tamamlandı")
        except Exception as e:
            warnings.append(f"Product analysis hatası: {str(e)}")
            logger.error("Product analysis hatası: %s", e)
    else:
        warnings.append("Ürün verisi sağlanmadı, ürün analizi atlandı")

    # Step 3: Campaign generation
    logger.info("Step 3: Campaign generation başlatılıyor...")
    
    # Prompt'u daha vurgulu hale getir
    enhanced_prompt = f"""
KULLANICI TALEBİ (ÖNCELİKLİ): {prompt}

Bu talebi dikkate alarak kampanya oluştur. Kullanıcının istediği kampanya türü, hedef ve yaklaşımı kullan.
"""
    
    campaign_payload = {
        "prompt": enhanced_prompt,
        "customerData": customer_insight,
        "productData": product_insight,
    }
    
    logger.info(f"Campaign payload - enhanced prompt: {enhanced_prompt[:150]}")

    try:
        campaign_result = invoke_agentcore_runtime(CAMPAIGN_AGENT_ARN, campaign_payload)
        logger.info("✓ Campaign generation tamamlandı")
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
