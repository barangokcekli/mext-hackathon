"""
DynamoDB Client for Customer Segment Agent

Müşteri verilerini DynamoDB'den çekmek için yardımcı fonksiyonlar.

Table Schema:
- customers: Müşteri bilgileri (customerId, age, gender, city, region, vb.)
- orders: Sipariş geçmişi (orderId, customerId, productId, amount, date, vb.)
- regions: Bölge bilgileri (regionName, climateType, medianBasket, trend)
"""

import logging
from typing import Any, Dict, List, Optional
from decimal import Decimal
import json

import boto3
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB operations for customer data."""

    def __init__(self, region_name: str = "us-west-2"):
        """
        Initialize DynamoDB client.
        
        Args:
            region_name: AWS region
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.customers_table = self.dynamodb.Table("Customers")
        self.orders_table = self.dynamodb.Table("Orders")
        self.regions_table = self.dynamodb.Table("Regions")

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Müşteri bilgilerini DynamoDB'den çeker.
        
        Args:
            customer_id: Müşteri ID (örn: "C-1001")
            
        Returns:
            Müşteri verisi veya None
        """
        try:
            response = self.customers_table.get_item(Key={"customerId": customer_id})
            item = response.get("Item")
            
            if item:
                return self._convert_decimals(item)
            
            logger.warning(f"Customer not found: {customer_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching customer {customer_id}: {e}")
            raise

    def get_customer_orders(self, customer_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Müşterinin sipariş geçmişini çeker.
        
        Args:
            customer_id: Müşteri ID
            limit: Maksimum sipariş sayısı
            
        Returns:
            Sipariş listesi
        """
        try:
            response = self.orders_table.query(
                IndexName="CustomerIdIndex",
                KeyConditionExpression=Key("customerId").eq(customer_id),
                Limit=limit,
                ScanIndexForward=False  # En yeni siparişler önce
            )
            
            items = response.get("Items", [])
            return [self._convert_decimals(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error fetching orders for {customer_id}: {e}")
            return []

    def get_region(self, region_name: str) -> Optional[Dict[str, Any]]:
        """
        Bölge bilgilerini çeker.
        
        Args:
            region_name: Bölge adı (örn: "Marmara")
            
        Returns:
            Bölge verisi veya None
        """
        try:
            response = self.regions_table.get_item(Key={"regionName": region_name})
            item = response.get("Item")
            
            if item:
                return self._convert_decimals(item)
            
            logger.warning(f"Region not found: {region_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching region {region_name}: {e}")
            return None

    def build_customer_payload(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Customer Segment Agent için tam payload oluşturur.
        
        Args:
            customer_id: Müşteri ID
            
        Returns:
            Agent payload formatında müşteri verisi
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return None
        
        # Orders tablosu yoksa boş liste kullan
        try:
            orders = self.get_customer_orders(customer_id)
        except Exception as e:
            logger.warning(f"Could not fetch orders: {e}")
            orders = []
        
        region_name = customer.get("region", "Marmara")
        region = self.get_region(region_name)
        
        # Product history oluştur
        product_history = []
        for order in orders:
            product_history.append({
                "productId": order.get("productId"),
                "category": order.get("category"),
                "amount": order.get("amount"),
                "date": order.get("orderDate")
            })
        
        # Region data - 'name' key'ini 'regionName'den al
        region_data = {
            "name": region.get("regionName", region_name) if region else region_name,
            "climateType": region.get("climateType", "Temperate") if region else "Temperate",
            "medianBasket": region.get("medianBasket", 75.0) if region else 75.0,
            "trend": region.get("trend", "SKINCARE") if region else "SKINCARE"
        }
        
        payload = {
            "customerId": customer_id,
            "city": customer.get("city"),
            "customer": {
                "age": customer.get("age"),
                "gender": customer.get("gender"),
                "registeredAt": customer.get("registeredAt"),
                "productHistory": product_history
            },
            "region": region_data
        }
        
        return payload

    @staticmethod
    def _convert_decimals(obj: Any) -> Any:
        """
        DynamoDB Decimal tiplerini Python float/int'e dönüştürür.
        
        Args:
            obj: DynamoDB response object
            
        Returns:
            Converted object
        """
        if isinstance(obj, list):
            return [DynamoDBClient._convert_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: DynamoDBClient._convert_decimals(value) for key, value in obj.items()}
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj


# Singleton instance
_dynamodb_client: Optional[DynamoDBClient] = None


def get_dynamodb_client(region_name: str = "us-west-2") -> DynamoDBClient:
    """
    DynamoDB client singleton instance döndürür.
    
    Args:
        region_name: AWS region
        
    Returns:
        DynamoDBClient instance
    """
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient(region_name=region_name)
    return _dynamodb_client
