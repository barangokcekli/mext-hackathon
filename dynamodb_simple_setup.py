"""
Simple DynamoDB Setup - Sadece data yükleme için
"""

import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")


def convert_floats(obj):
    """Float'ları Decimal'e çevir"""
    if isinstance(obj, list):
        return [convert_floats(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def load_customers():
    """Customers data'yı yükle"""
    table = dynamodb.Table("Customers")
    
    with open("customer-segment-agent/mock-data/farmasi/customers-100.json", "r", encoding="utf-8") as f:
        customers = json.load(f)
    
    print(f"Loading {len(customers)} customers...")
    
    with table.batch_writer() as batch:
        for customer in customers:
            customer_converted = convert_floats(customer)
            batch.put_item(Item=customer_converted)
    
    print(f"✓ {len(customers)} müşteri yüklendi")


def load_products():
    """Products data'yı yükle"""
    table = dynamodb.Table("Products")
    
    with open("product-agent/data/products_2.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    products = data.get("products", [])
    print(f"Loading {len(products)} products...")
    
    with table.batch_writer() as batch:
        for product in products:
            product["tenantId"] = "farmasi"
            product_converted = convert_floats(product)
            batch.put_item(Item=product_converted)
    
    print(f"✓ {len(products)} ürün yüklendi")


if __name__ == "__main__":
    print("=== DynamoDB Data Loading ===")
    
    try:
        load_customers()
    except Exception as e:
        print(f"Customer loading error: {e}")
    
    try:
        load_products()
    except Exception as e:
        print(f"Product loading error: {e}")
    
    print("=== Done ===")
