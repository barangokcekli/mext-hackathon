"""
Basit DynamoDB Table Oluşturma
"""

import boto3

dynamodb = boto3.client("dynamodb", region_name="us-west-2")

def create_customers_table():
    try:
        dynamodb.create_table(
            TableName="Customers",
            KeySchema=[{"AttributeName": "customerId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "customerId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        print("✓ Customers table created")
    except Exception as e:
        print(f"Customers table: {e}")


def create_products_table():
    try:
        dynamodb.create_table(
            TableName="Products",
            KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "productId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        print("✓ Products table created")
    except Exception as e:
        print(f"Products table: {e}")


if __name__ == "__main__":
    print("Creating tables...")
    create_customers_table()
    create_products_table()
    print("Done!")
