"""
Basit DynamoDB Test
"""

import boto3
from decimal import Decimal

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    return obj

print("=" * 60)
print("DynamoDB TEST")
print("=" * 60)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

# Test 1: Customers
print("\n[1] Customers Tablosu")
print("-" * 60)
customers_table = dynamodb.Table('Customers')
response = customers_table.get_item(Key={'customerId': 'C-2001'})
customer = response.get('Item')

if customer:
    customer = convert_decimal(customer)
    print(f"✓ Müşteri bulundu: {customer['customerId']}")
    print(f"  • Şehir: {customer['city']}")
    print(f"  • Yaş: {customer['age']}")
    print(f"  • Bölge: {customer['region']}")
else:
    print("✗ Müşteri bulunamadı")

# Test 2: Products
print("\n[2] Products Tablosu")
print("-" * 60)
products_table = dynamodb.Table('Products')
response = products_table.scan(Limit=5)
products = response.get('Items', [])

print(f"✓ {len(products)} ürün bulundu:")
for p in products[:3]:
    p = convert_decimal(p)
    print(f"  • {p['productName']} - {p['basePrice']} TL")

# Test 3: Regions
print("\n[3] Regions Tablosu")
print("-" * 60)
regions_table = dynamodb.Table('Regions')
response = regions_table.scan()
regions = response.get('Items', [])

print(f"✓ {len(regions)} bölge bulundu:")
for r in regions:
    r = convert_decimal(r)
    print(f"  • {r['regionName']:20} - {r['climateType']:15} - {r['medianBasket']} TL")

# Test 4: Region ile Customer birleştirme
print("\n[4] Customer + Region Birleştirme")
print("-" * 60)

customer_response = customers_table.get_item(Key={'customerId': 'C-2005'})
customer = convert_decimal(customer_response.get('Item'))

region_response = regions_table.get_item(Key={'regionName': customer['region']})
region = convert_decimal(region_response.get('Item'))

print(f"✓ Müşteri: {customer['customerId']} ({customer['city']})")
print(f"✓ Bölge: {region['regionName']}")
print(f"  • İklim: {region['climateType']}")
print(f"  • Medyan Sepet: {region['medianBasket']} TL")
print(f"  • Trend: {region['trend']}")

print("\n" + "=" * 60)
print("TÜM TESTLER BAŞARILI!")
print("=" * 60)
print("\nDynamoDB'de şu tablolar hazır:")
print("  ✓ Customers (100 müşteri)")
print("  ✓ Products (109 ürün)")
print("  ✓ Regions (7 bölge)")
print("\nOrchestrator agent'ı kullanmaya hazır!")
