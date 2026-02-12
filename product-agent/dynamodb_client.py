"""
DynamoDB Client for Product Analysis Agent

Ürün verilerini DynamoDB'den çekmek için yardımcı fonksiyonlar.

Table Schema:
- products: Ürün bilgileri (productId, name, category, price, stock, vb.)
- orders: Sipariş geçmişi (orderId, productId, customerId, quantity, date, vb.)
- climate_data: İklim bilgileri (city, avgTempC, humidity, season)
"""

import logging
from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger(__name__)


class ProductDynamoDBClient:
    """DynamoDB operations for product data."""

    def __init__(self, region_name: str = "us-west-2"):
        """
        Initialize DynamoDB client.
        
        Args:
            region_name: AWS region
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.products_table = self.dynamodb.Table("Products")
        self.orders_table = self.dynamodb.Table("Orders")
        self.climate_table = self.dynamodb.Table("ClimateData")

    def get_products(self, tenant_id: str = "farmasi", limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Tenant'a ait tüm ürünleri çeker.
        
        Args:
            tenant_id: Tenant ID
            limit: Maksimum ürün sayısı
            
        Returns:
            Ürün listesi
        """
        try:
            # TenantIdIndex yoksa scan kullan
            response = self.products_table.scan(
                FilterExpression=Attr('tenantId').eq(tenant_id),
                Limit=limit
            )
            
            items = response.get("Items", [])
            return [self._convert_decimals(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error fetching products for tenant {tenant_id}: {e}")
            # Fallback: scan without filter
            try:
                response = self.products_table.scan(Limit=limit)
                items = response.get("Items", [])
                return [self._convert_decimals(item) for item in items]
            except:
                return []

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Tek bir ürünü çeker.
        
        Args:
            product_id: Ürün ID
            
        Returns:
            Ürün verisi veya None
        """
        try:
            response = self.products_table.get_item(Key={"productId": product_id})
            item = response.get("Item")
            
            if item:
                return self._convert_decimals(item)
            
            logger.warning(f"Product not found: {product_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None

    def get_order_history(self, days: int = 90, limit: int = 10000) -> List[Dict[str, Any]]:
        """
        Son N günün sipariş geçmişini çeker.
        
        Args:
            days: Kaç günlük geçmiş
            limit: Maksimum sipariş sayısı
            
        Returns:
            Sipariş listesi
        """
        try:
            # Scan with filter (production'da date index kullanılmalı)
            response = self.orders_table.scan(Limit=limit)
            
            items = response.get("Items", [])
            return [self._convert_decimals(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error fetching order history: {e}")
            return []

    def get_climate_data(self, cities: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Şehirlerin iklim verilerini çeker.
        
        Args:
            cities: Şehir listesi (None ise tüm şehirler)
            
        Returns:
            {city: climate_data} formatında dict
        """
        try:
            if cities:
                # Batch get
                climate_data = {}
                for city in cities:
                    response = self.climate_table.get_item(Key={"city": city})
                    item = response.get("Item")
                    if item:
                        climate_data[city] = self._convert_decimals(item)
                return climate_data
            else:
                # Scan all
                response = self.climate_table.scan()
                items = response.get("Items", [])
                return {
                    item["city"]: self._convert_decimals(item)
                    for item in items
                }
                
        except Exception as e:
            logger.error(f"Error fetching climate data: {e}")
            return {}

    def build_product_payload(
        self,
        tenant_id: str = "farmasi",
        current_month: int = None
    ) -> Dict[str, Any]:
        """
        Product Analysis Agent için tam payload oluşturur.
        
        Args:
            tenant_id: Tenant ID
            current_month: Mevcut ay (1-12), None ise şimdiki ay
            
        Returns:
            Agent payload formatında ürün verisi
        """
        if current_month is None:
            current_month = datetime.now().month
        
        products = self.get_products(tenant_id)
        order_history = self.get_order_history()
        climate_data = self.get_climate_data()
        
        payload = {
            "tenantId": tenant_id,
            "products": products,
            "orderHistory": order_history,
            "currentMonth": current_month,
            "climateData": climate_data
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
            return [ProductDynamoDBClient._convert_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: ProductDynamoDBClient._convert_decimals(value) for key, value in obj.items()}
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj


# Singleton instance
_product_dynamodb_client: Optional[ProductDynamoDBClient] = None


def get_product_dynamodb_client(region_name: str = "us-west-2") -> ProductDynamoDBClient:
    """
    Product DynamoDB client singleton instance döndürür.
    
    Args:
        region_name: AWS region
        
    Returns:
        ProductDynamoDBClient instance
    """
    global _product_dynamodb_client
    if _product_dynamodb_client is None:
        _product_dynamodb_client = ProductDynamoDBClient(region_name=region_name)
    return _product_dynamodb_client
