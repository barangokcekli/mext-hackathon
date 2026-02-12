"""
Orchestrator DynamoDB Integration Test
Bu script orchestrator'ın DynamoDB'den veri çekme yeteneğini test eder
"""

import sys
import json
import os

# Add specific paths
customer_path = os.path.join(os.path.dirname(__file__), 'customer-segment-agent')
product_path = os.path.join(os.path.dirname(__file__), 'product-agent')

sys.path.insert(0, customer_path)

print("=" * 70)
print("ORCHESTRATOR + DYNAMODB ENTEGRASYON TESTİ")
print("=" * 70)

# Test 1: DynamoDB'den Customer Data Çekme
print("\n[1] Customer Data - DynamoDB'den Çekiliyor...")
print("-" * 70)

try:
    # Import from customer-segment-agent
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "customer_dynamodb_client",
        os.path.join(customer_path, "dynamodb_client.py")
    )
    customer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(customer_module)
    
    customer_client = customer_module.DynamoDBClient(region_name='us-west-2')
    customer_payload = customer_client.build_customer_payload('C-2001')
    
    if customer_payload:
        print("✓ Customer data başarıyla çekildi:")
        print(f"  • Customer ID: {customer_payload['customerId']}")
        print(f"  • Şehir: {customer_payload['city']}")
        print(f"  • Yaş: {customer_payload['customer']['age']}")
        print(f"  • Cinsiyet: {customer_payload['customer']['gender']}")
        print(f"  • Bölge: {customer_payload['region']['name']}")
        print(f"  • Bölge İklimi: {customer_payload['region']['climateType']}")
        print(f"  • Medyan Sepet: {customer_payload['region']['medianBasket']} TL")
        
        # Save for inspection
        with open('customer_payload_from_dynamodb.json', 'w', encoding='utf-8') as f:
            json.dump(customer_payload, f, indent=2, ensure_ascii=False)
        print("\n  → Payload kaydedildi: customer_payload_from_dynamodb.json")
    else:
        print("✗ Customer data çekilemedi")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ HATA: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: DynamoDB'den Product Data Çekme
print("\n[2] Product Data - DynamoDB'den Çekiliyor...")
print("-" * 70)

try:
    # Import from product-agent
    spec = importlib.util.spec_from_file_location(
        "product_dynamodb_client",
        os.path.join(product_path, "dynamodb_client.py")
    )
    product_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(product_module)
    
    product_client = product_module.ProductDynamoDBClient(region_name='us-west-2')
    product_payload = product_client.build_product_payload(tenant_id='farmasi')
    
    if product_payload:
        print("✓ Product data başarıyla çekildi:")
        print(f"  • Tenant: {product_payload['tenantId']}")
        print(f"  • Toplam Ürün: {len(product_payload['products'])}")
        print(f"  • Order History: {len(product_payload['orderHistory'])} kayıt")
        print(f"  • Mevcut Ay: {product_payload['currentMonth']}")
        
        if product_payload['products']:
            print("\n  İlk 5 Ürün:")
            for i, p in enumerate(product_payload['products'][:5], 1):
                print(f"    {i}. {p['productName']} - {p['basePrice']} TL")
        
        # Save for inspection
        with open('product_payload_from_dynamodb.json', 'w', encoding='utf-8') as f:
            json.dump(product_payload, f, indent=2, ensure_ascii=False, default=str)
        print("\n  → Payload kaydedildi: product_payload_from_dynamodb.json")
    else:
        print("✗ Product data çekilemedi")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ HATA: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Orchestrator Payload Simülasyonu
print("\n[3] Orchestrator Payload Simülasyonu")
print("-" * 70)

orchestrator_payload = {
    "prompt": "Kış kampanyası oluştur - müşteriye özel ürün önerileri",
    "customerData": customer_payload,
    "productData": product_payload,
    "useLLM": False  # Deterministik mod
}

print("✓ Orchestrator payload hazırlandı:")
print(f"  • Prompt: {orchestrator_payload['prompt']}")
print(f"  • Customer Data: ✓ (DynamoDB'den)")
print(f"  • Product Data: ✓ (DynamoDB'den)")
print(f"  • LLM Mode: {orchestrator_payload['useLLM']}")

# Save orchestrator payload
with open('orchestrator_payload_dynamodb.json', 'w', encoding='utf-8') as f:
    json.dump(orchestrator_payload, f, indent=2, ensure_ascii=False, default=str)
print("\n  → Payload kaydedildi: orchestrator_payload_dynamodb.json")

# Test 4: Orchestrator Invoke Simülasyonu (useDynamoDB flag ile)
print("\n[4] Orchestrator useDynamoDB Flag Testi")
print("-" * 70)

orchestrator_dynamodb_payload = {
    "prompt": "Kış kampanyası oluştur",
    "customerId": "C-2001",      # DynamoDB'den çekilecek
    "tenantId": "farmasi",       # DynamoDB'den çekilecek
    "useDynamoDB": True,         # DynamoDB mode aktif
    "useLLM": False
}

print("✓ Orchestrator DynamoDB payload hazırlandı:")
print(f"  • Prompt: {orchestrator_dynamodb_payload['prompt']}")
print(f"  • Customer ID: {orchestrator_dynamodb_payload['customerId']} (DynamoDB'den çekilecek)")
print(f"  • Tenant ID: {orchestrator_dynamodb_payload['tenantId']} (DynamoDB'den çekilecek)")
print(f"  • Use DynamoDB: {orchestrator_dynamodb_payload['useDynamoDB']}")
print(f"  • LLM Mode: {orchestrator_dynamodb_payload['useLLM']}")

with open('orchestrator_dynamodb_flag_payload.json', 'w', encoding='utf-8') as f:
    json.dump(orchestrator_dynamodb_payload, f, indent=2, ensure_ascii=False)
print("\n  → Payload kaydedildi: orchestrator_dynamodb_flag_payload.json")

# Summary
print("\n" + "=" * 70)
print("TEST SONUÇLARI")
print("=" * 70)
print("✓ Customer data DynamoDB'den başarıyla çekildi")
print("✓ Product data DynamoDB'den başarıyla çekildi")
print("✓ Orchestrator payload'ları hazırlandı")
print("\nOluşturulan Dosyalar:")
print("  1. customer_payload_from_dynamodb.json")
print("  2. product_payload_from_dynamodb.json")
print("  3. orchestrator_payload_dynamodb.json")
print("  4. orchestrator_dynamodb_flag_payload.json")
print("\n" + "=" * 70)
print("DynamoDB ENTEGRASYONU ÇALIŞIYOR! ✓")
print("=" * 70)
print("\nOrchestrator'ı çalıştırmak için:")
print("  1. Agent'ları AgentCore Runtime'a deploy edin")
print("  2. orchestrator_agent.py'yi invoke edin:")
print("     from orchestrator_agent import invoke")
print("     result = invoke(orchestrator_dynamodb_payload)")
print("=" * 70)
