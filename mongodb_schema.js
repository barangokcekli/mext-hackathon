// ============================================================================
// Çoklu Ajan Kampanya Zekası Sistemi - MongoDB Şeması
// Multi-Tenant Mimari - Document-Based Design
// ============================================================================

// ============================================================================
// 1. TENANT COLLECTION
// ============================================================================

db.createCollection("tenants", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tenantId", "companyName", "sector", "contactEmail", "apiKey"],
      properties: {
        tenantId: {
          bsonType: "string",
          description: "Benzersiz tenant kimliği"
        },
        companyName: {
          bsonType: "string",
          description: "Şirket adı"
        },
        sector: {
          bsonType: "string",
          description: "Sektör"
        },
        contactEmail: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        apiKey: {
          bsonType: "string",
          description: "API erişim anahtarı"
        },
        createdAt: {
          bsonType: "date"
        },
        updatedAt: {
          bsonType: "date"
        },
        isActive: {
          bsonType: "bool"
        },
        settings: {
          bsonType: "object",
          properties: {
            marginFloor: { bsonType: "double", minimum: 0, maximum: 100 },
            stockDaysThreshold: { bsonType: "int", minimum: 0 },
            maxRecommendations: { bsonType: "int", minimum: 1 },
            currency: { bsonType: "string" }
          }
        }
      }
    }
  }
});

// Indexes
db.tenants.createIndex({ tenantId: 1 }, { unique: true });
db.tenants.createIndex({ apiKey: 1 }, { unique: true });
db.tenants.createIndex({ isActive: 1 });
db.tenants.createIndex({ createdAt: -1 });

// Örnek döküman
const exampleTenant = {
  tenantId: "farmasi",
  companyName: "Farmasi Türkiye",
  sector: "cosmetics",
  contactEmail: "info@farmasi.com.tr",
  apiKey: "frm_a8f3d9c2b1e4f7a6",
  createdAt: new Date("2026-01-15T08:00:00Z"),
  updatedAt: new Date("2026-01-15T08:00:00Z"),
  isActive: true,
  settings: {
    marginFloor: 25.0,
    stockDaysThreshold: 60,
    maxRecommendations: 3,
    currency: "TRY"
  }
};

// ============================================================================
// 2. REGIONS COLLECTION (Paylaşımlı)
// ============================================================================

db.createCollection("regions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "climateType", "medianBasket", "trend", "cities", "seasonalNeeds"],
      properties: {
        name: { bsonType: "string" },
        climateType: { 
          enum: ["Metropol", "Sıcak-Nemli", "Sıcak-Kuru", "Soğuk"]
        },
        medianBasket: { bsonType: "double", minimum: 0 },
        trend: { 
          enum: ["MAKEUP", "SKINCARE", "FRAGRANCE", "PERSONALCARE", "HAIRCARE", "WELLNESS"]
        },
        cities: {
          bsonType: "array",
          items: { bsonType: "string" }
        },
        seasonalNeeds: {
          bsonType: "object",
          properties: {
            winter: { bsonType: "array", items: { bsonType: "string" } },
            summer: { bsonType: "array", items: { bsonType: "string" } },
            spring: { bsonType: "array", items: { bsonType: "string" } },
            autumn: { bsonType: "array", items: { bsonType: "string" } }
          }
        }
      }
    }
  }
});

// Indexes
db.regions.createIndex({ name: 1 }, { unique: true });
db.regions.createIndex({ "cities": 1 });
db.regions.createIndex({ climateType: 1 });

// Örnek döküman
const exampleRegion = {
  name: "Marmara",
  climateType: "Metropol",
  medianBasket: 85.00,
  trend: "SKINCARE",
  cities: ["Istanbul", "Bursa", "Kocaeli"],
  seasonalNeeds: {
    winter: ["nemlendirici", "dudak-bakım", "el-kremi"],
    summer: ["SPF", "hafif-nemlendirici", "mat-makyaj"],
    spring: ["anti-aging", "serum", "temizleyici"],
    autumn: ["onarıcı", "besleyici-krem", "maske"]
  }
};

// ============================================================================
// 3. PRODUCTS COLLECTION (Tenant Bazlı)
// ============================================================================

db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["productId", "tenantId", "productName", "category", "unitCost", "unitPrice"],
      properties: {
        productId: { bsonType: "string" },
        tenantId: { bsonType: "string" },
        productName: { bsonType: "string" },
        category: {
          enum: ["MAKEUP", "SKINCARE", "FRAGRANCE", "PERSONALCARE", "HAIRCARE", "WELLNESS"]
        },
        subcategory: { bsonType: "string" },
        tags: {
          bsonType: "array",
          items: { bsonType: "string" }
        },
        season: {
          enum: ["all", "winter", "summer", "spring", "autumn"]
        },
        currentStock: { bsonType: "int", minimum: 0 },
        last30DaysSales: { bsonType: "int", minimum: 0 },
        unitCost: { bsonType: "double", minimum: 0 },
        unitPrice: { bsonType: "double", minimum: 0 },
        sourceUrl: { bsonType: "string" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" },
        
        // Türetilen metrikler (cache)
        derived: {
          bsonType: "object",
          properties: {
            dailySales: { bsonType: "double" },
            stockDays: { bsonType: "int" },
            inventoryPressure: { bsonType: "bool" },
            grossMarginPercent: { bsonType: "double" },
            maxDiscountPercent: { bsonType: "double" },
            stockSegment: { 
              enum: ["Hero", "Normal", "SlowMover", "DeadStock"]
            }
          }
        }
      }
    }
  }
});

// Indexes
db.products.createIndex({ productId: 1, tenantId: 1 }, { unique: true });
db.products.createIndex({ tenantId: 1, category: 1 });
db.products.createIndex({ tenantId: 1, season: 1 });
db.products.createIndex({ tenantId: 1, currentStock: 1 });
db.products.createIndex({ "tags": 1 });
db.products.createIndex({ "derived.stockSegment": 1 });

// Örnek döküman
const exampleProduct = {
  productId: "P-2001",
  tenantId: "farmasi",
  productName: "Dr. C. Tuna Tea Tree Face Wash",
  category: "SKINCARE",
  subcategory: "Yüz Temizleme",
  tags: ["temizleyici", "jel", "akne", "arındırıcı"],
  season: "all",
  currentStock: 900,
  last30DaysSales: 75,
  unitCost: 20.00,
  unitPrice: 59.90,
  sourceUrl: "https://farmasi.com.tr",
  createdAt: new Date(),
  updatedAt: new Date(),
  derived: {
    dailySales: 2.5,
    stockDays: 360,
    inventoryPressure: true,
    grossMarginPercent: 66.61,
    maxDiscountPercent: 41.61,
    stockSegment: "SlowMover"
  }
};

// ============================================================================
// 4. CUSTOMERS COLLECTION (Tenant Bazlı - Embedded Product History)
// ============================================================================

db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customerId", "tenantId", "city", "registeredAt"],
      properties: {
        customerId: { bsonType: "string" },
        tenantId: { bsonType: "string" },
        city: { bsonType: "string" },
        region: { bsonType: "string" },
        age: { bsonType: "int", minimum: 0, maximum: 120 },
        gender: { enum: ["F", "M", "U"] },
        registeredAt: { bsonType: "date" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" },
        
        // Ürün bazlı alışveriş geçmişi (embedded)
        productHistory: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["productId", "category", "totalQuantity", "totalSpent", "orderCount"],
            properties: {
              productId: { bsonType: "string" },
              category: { bsonType: "string" },
              totalQuantity: { bsonType: "int", minimum: 0 },
              totalSpent: { bsonType: "double", minimum: 0 },
              orderCount: { bsonType: "int", minimum: 0 },
              firstPurchase: { bsonType: "date" },
              lastPurchase: { bsonType: "date" },
              avgDaysBetween: { bsonType: ["int", "null"] }
            }
          }
        },
        
        // Türetilen metrikler (cache)
        derived: {
          bsonType: "object",
          properties: {
            ageSegment: { enum: ["GenZ", "GençYetişkin", "Yetişkin", "Olgun"] },
            churnSegment: { enum: ["Active", "Warm", "AtRisk"] },
            valueSegment: { enum: ["HighValue", "Standard"] },
            loyaltyTier: { enum: ["Platin", "Altın", "Gümüş", "Bronz"] },
            affinityCategory: { bsonType: "string" },
            affinityType: { enum: ["Odaklı", "Keşifçi"] },
            diversityProfile: { enum: ["Kaşif", "Dengeli", "Sadık"] },
            estimatedBudget: { bsonType: "double" },
            avgBasket: { bsonType: "double" },
            avgMonthlySpend: { bsonType: "double" },
            lastPurchaseDaysAgo: { bsonType: "int" },
            totalOrders: { bsonType: "int" },
            totalSpent: { bsonType: "double" },
            membershipDays: { bsonType: "int" },
            uniqueProducts: { bsonType: "int" }
          }
        }
      }
    }
  }
});

// Indexes
db.customers.createIndex({ customerId: 1, tenantId: 1 }, { unique: true });
db.customers.createIndex({ tenantId: 1, city: 1 });
db.customers.createIndex({ tenantId: 1, age: 1 });
db.customers.createIndex({ tenantId: 1, gender: 1 });
db.customers.createIndex({ "productHistory.productId": 1 });
db.customers.createIndex({ "productHistory.lastPurchase": -1 });
db.customers.createIndex({ "derived.churnSegment": 1, "derived.valueSegment": 1 });

// Örnek döküman
const exampleCustomer = {
  customerId: "C-1001",
  tenantId: "farmasi",
  city: "Istanbul",
  region: "Marmara",
  age: 32,
  gender: "F",
  registeredAt: new Date("2024-03-15"),
  createdAt: new Date(),
  updatedAt: new Date(),
  productHistory: [
    {
      productId: "P-2001",
      category: "SKINCARE",
      totalQuantity: 8,
      totalSpent: 479.20,
      orderCount: 8,
      firstPurchase: new Date("2025-01-15"),
      lastPurchase: new Date("2026-01-20"),
      avgDaysBetween: 30
    },
    {
      productId: "P-2004",
      category: "SKINCARE",
      totalQuantity: 7,
      totalSpent: 454.30,
      orderCount: 5,
      firstPurchase: new Date("2025-02-10"),
      lastPurchase: new Date("2026-02-01"),
      avgDaysBetween: 45
    }
  ],
  derived: {
    ageSegment: "GençYetişkin",
    churnSegment: "Active",
    valueSegment: "HighValue",
    loyaltyTier: "Altın",
    affinityCategory: "SKINCARE",
    affinityType: "Odaklı",
    diversityProfile: "Dengeli",
    estimatedBudget: 102.60,
    avgBasket: 85.50,
    avgMonthlySpend: 171.00,
    lastPurchaseDaysAgo: 12,
    totalOrders: 14,
    totalSpent: 988.40,
    membershipDays: 335,
    uniqueProducts: 6
  }
};

// ============================================================================
// 5. CAMPAIGNS COLLECTION
// ============================================================================

db.createCollection("campaigns", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["campaignId", "tenantId", "city", "objective"],
      properties: {
        campaignId: { bsonType: "string" },
        tenantId: { bsonType: "string" },
        customerId: { bsonType: ["string", "null"] },
        city: { bsonType: "string" },
        region: { bsonType: "string" },
        
        objective: {
          enum: ["IncreaseRevenue", "ClearOverstock", "CustomerRetention"]
        },
        event: { bsonType: ["string", "null"] },
        
        targetSegment: {
          bsonType: "object",
          properties: {
            churn: { enum: ["Active", "Warm", "AtRisk"] },
            value: { enum: ["HighValue", "Standard"] },
            affinity: { bsonType: "string" },
            ageSegment: { bsonType: "string" },
            climateType: { bsonType: "string" }
          }
        },
        
        strategy: {
          bsonType: "object",
          required: ["type"],
          properties: {
            type: { bsonType: "string" },
            description: { bsonType: "string" },
            discountPercent: { bsonType: "double" },
            marginCheck: {
              bsonType: "object",
              properties: {
                floor: { bsonType: "double" },
                passed: { bsonType: "bool" }
              }
            },
            regionNote: { bsonType: "string" }
          }
        },
        
        products: {
          bsonType: "object",
          properties: {
            hero: {
              bsonType: "array",
              items: {
                bsonType: "object",
                properties: {
                  productId: { bsonType: "string" },
                  role: { bsonType: "string" },
                  discountPercent: { bsonType: "double" }
                }
              }
            },
            clearance: {
              bsonType: "array",
              items: {
                bsonType: "object",
                properties: {
                  productId: { bsonType: "string" },
                  role: { bsonType: "string" },
                  discountPercent: { bsonType: "double" }
                }
              }
            }
          }
        },
        
        messaging: {
          bsonType: "object",
          properties: {
            headline: { bsonType: "string" },
            subtext: { bsonType: "string" },
            eventTheme: { bsonType: "string" }
          }
        },
        
        recommendations: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              productId: { bsonType: "string" },
              productName: { bsonType: "string" },
              reason: { bsonType: "string" },
              matchScore: { bsonType: "double" },
              matchFactors: {
                bsonType: "object",
                properties: {
                  categoryMatch: { bsonType: "double" },
                  seasonMatch: { bsonType: "double" },
                  ageMatch: { bsonType: "double" },
                  complementaryBonus: { bsonType: "double" },
                  diversityMatch: { bsonType: "double" }
                }
              }
            }
          }
        },
        
        metadata: {
          bsonType: "object",
          properties: {
            generatedAt: { bsonType: "date" },
            agentVersion: { bsonType: "string" }
          }
        }
      }
    }
  }
});

// Indexes
db.campaigns.createIndex({ campaignId: 1 }, { unique: true });
db.campaigns.createIndex({ tenantId: 1, "metadata.generatedAt": -1 });
db.campaigns.createIndex({ tenantId: 1, customerId: 1 });
db.campaigns.createIndex({ tenantId: 1, objective: 1 });
db.campaigns.createIndex({ city: 1 });

// ============================================================================
// 6. CATALOG_SOURCES COLLECTION
// ============================================================================

db.createCollection("catalogSources", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tenantId", "url"],
      properties: {
        tenantId: { bsonType: "string" },
        url: { bsonType: "string" },
        lastScraped: { bsonType: ["date", "null"] },
        productCount: { bsonType: "int", minimum: 0 },
        status: { enum: ["pending", "success", "failed"] },
        errorMessage: { bsonType: ["string", "null"] },
        selectors: {
          bsonType: "object",
          properties: {
            productCard: { bsonType: "string" },
            name: { bsonType: "string" },
            price: { bsonType: "string" },
            category: { bsonType: "string" },
            image: { bsonType: "string" }
          }
        },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

// Indexes
db.catalogSources.createIndex({ tenantId: 1, url: 1 });
db.catalogSources.createIndex({ lastScraped: -1 });
db.catalogSources.createIndex({ status: 1 });

// ============================================================================
// 7. IMPORT_HISTORY COLLECTION
// ============================================================================

db.createCollection("importHistory", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tenantId", "dataType"],
      properties: {
        tenantId: { bsonType: "string" },
        dataType: { enum: ["products", "customers", "catalog_scrape"] },
        totalRecords: { bsonType: "int", minimum: 0 },
        importedRecords: { bsonType: "int", minimum: 0 },
        skippedRecords: { bsonType: "int", minimum: 0 },
        errorRecords: { bsonType: "int", minimum: 0 },
        fileName: { bsonType: ["string", "null"] },
        fileSizeKb: { bsonType: ["int", "null"] },
        status: { enum: ["pending", "processing", "completed", "failed"] },
        errorLog: { bsonType: ["string", "null"] },
        startedAt: { bsonType: "date" },
        completedAt: { bsonType: ["date", "null"] }
      }
    }
  }
});

// Indexes
db.importHistory.createIndex({ tenantId: 1, startedAt: -1 });
db.importHistory.createIndex({ status: 1 });

// ============================================================================
// 8. AGGREGATION PIPELINE ÖRNEKLERI
// ============================================================================

// Müşteri segmentasyon özeti
const customerSegmentationPipeline = [
  {
    $match: { tenantId: "farmasi" }
  },
  {
    $group: {
      _id: {
        churn: "$derived.churnSegment",
        value: "$derived.valueSegment"
      },
      count: { $sum: 1 },
      avgSpent: { $avg: "$derived.totalSpent" },
      avgBasket: { $avg: "$derived.avgBasket" }
    }
  },
  {
    $sort: { "_id.churn": 1, "_id.value": 1 }
  }
];

// Stok durumu özeti
const stockStatusPipeline = [
  {
    $match: { tenantId: "farmasi" }
  },
  {
    $group: {
      _id: "$derived.stockSegment",
      count: { $sum: 1 },
      totalStock: { $sum: "$currentStock" },
      avgStockDays: { $avg: "$derived.stockDays" }
    }
  },
  {
    $sort: { "_id": 1 }
  }
];

// Kategori bazlı satış analizi
const categorySalesPipeline = [
  {
    $match: { tenantId: "farmasi" }
  },
  {
    $unwind: "$productHistory"
  },
  {
    $group: {
      _id: "$productHistory.category",
      totalRevenue: { $sum: "$productHistory.totalSpent" },
      totalQuantity: { $sum: "$productHistory.totalQuantity" },
      totalOrders: { $sum: "$productHistory.orderCount" },
      uniqueCustomers: { $addToSet: "$customerId" }
    }
  },
  {
    $project: {
      category: "$_id",
      totalRevenue: 1,
      totalQuantity: 1,
      totalOrders: 1,
      customerCount: { $size: "$uniqueCustomers" }
    }
  },
  {
    $sort: { totalRevenue: -1 }
  }
];

// Bölge bazlı performans
const regionPerformancePipeline = [
  {
    $match: { tenantId: "farmasi" }
  },
  {
    $group: {
      _id: "$region",
      customerCount: { $sum: 1 },
      totalRevenue: { $sum: "$derived.totalSpent" },
      avgBasket: { $avg: "$derived.avgBasket" },
      highValueCount: {
        $sum: {
          $cond: [{ $eq: ["$derived.valueSegment", "HighValue"] }, 1, 0]
        }
      }
    }
  },
  {
    $sort: { totalRevenue: -1 }
  }
];

// ============================================================================
// 9. UTILITY FUNCTIONS
// ============================================================================

// Müşteri türetilen metrikleri güncelleme
function updateCustomerDerivedMetrics(customerId, tenantId) {
  const customer = db.customers.findOne({ customerId, tenantId });
  
  if (!customer || !customer.productHistory || customer.productHistory.length === 0) {
    return;
  }
  
  const now = new Date();
  const registeredAt = customer.registeredAt;
  const membershipDays = Math.floor((now - registeredAt) / (1000 * 60 * 60 * 24));
  
  // Hesaplamalar
  const totalOrders = customer.productHistory.reduce((sum, p) => sum + p.orderCount, 0);
  const totalSpent = customer.productHistory.reduce((sum, p) => sum + p.totalSpent, 0);
  const avgBasket = totalSpent / totalOrders;
  const uniqueProducts = customer.productHistory.length;
  
  const lastPurchase = new Date(Math.max(...customer.productHistory.map(p => p.lastPurchase)));
  const lastPurchaseDaysAgo = Math.floor((now - lastPurchase) / (1000 * 60 * 60 * 24));
  
  // Segmentler
  let churnSegment = "Active";
  if (lastPurchaseDaysAgo > 60) churnSegment = "AtRisk";
  else if (lastPurchaseDaysAgo >= 30) churnSegment = "Warm";
  
  const region = db.regions.findOne({ cities: customer.city });
  const valueSegment = avgBasket > region.medianBasket ? "HighValue" : "Standard";
  
  let ageSegment = "Olgun";
  if (customer.age <= 25) ageSegment = "GenZ";
  else if (customer.age <= 35) ageSegment = "GençYetişkin";
  else if (customer.age <= 50) ageSegment = "Yetişkin";
  
  // Güncelleme
  db.customers.updateOne(
    { customerId, tenantId },
    {
      $set: {
        "derived.churnSegment": churnSegment,
        "derived.valueSegment": valueSegment,
        "derived.ageSegment": ageSegment,
        "derived.totalOrders": totalOrders,
        "derived.totalSpent": totalSpent,
        "derived.avgBasket": avgBasket,
        "derived.uniqueProducts": uniqueProducts,
        "derived.lastPurchaseDaysAgo": lastPurchaseDaysAgo,
        "derived.membershipDays": membershipDays,
        "derived.estimatedBudget": avgBasket * 1.2,
        updatedAt: now
      }
    }
  );
}

// Ürün türetilen metrikleri güncelleme
function updateProductDerivedMetrics(productId, tenantId) {
  const product = db.products.findOne({ productId, tenantId });
  
  if (!product) return;
  
  const dailySales = product.last30DaysSales / 30;
  const stockDays = dailySales > 0 ? Math.floor(product.currentStock / dailySales) : null;
  const inventoryPressure = stockDays > 60;
  const grossMarginPercent = ((product.unitPrice - product.unitCost) / product.unitPrice) * 100;
  const maxDiscountPercent = grossMarginPercent - 25;
  
  let stockSegment = "Normal";
  if (dailySales === 0 && product.currentStock > 0) {
    stockSegment = "DeadStock";
  } else if (stockDays > 60) {
    stockSegment = "SlowMover";
  } else if (stockDays <= 20) {
    stockSegment = "Hero";
  }
  
  db.products.updateOne(
    { productId, tenantId },
    {
      $set: {
        "derived.dailySales": dailySales,
        "derived.stockDays": stockDays,
        "derived.inventoryPressure": inventoryPressure,
        "derived.grossMarginPercent": grossMarginPercent,
        "derived.maxDiscountPercent": maxDiscountPercent,
        "derived.stockSegment": stockSegment,
        updatedAt: new Date()
      }
    }
  );
}

// ============================================================================
// 10. NOTLAR
// ============================================================================

/*
MONGODB AVANTAJLARI:
1. Esnek şema - JSON formatında veri saklama
2. Embedded documents - productHistory müşteri kaydında gömülü
3. Hızlı okuma - denormalize veri yapısı
4. Kolay ölçeklendirme - horizontal scaling
5. Aggregation pipeline - güçlü analiz yetenekleri

DEZAVANTAJLAR:
1. İlişkisel bütünlük - manuel kontrol gerekir
2. Transaction desteği - sınırlı (4.0+ ile gelişti)
3. Veri tutarlılığı - denormalize yapıda güncellemeler zor olabilir

KULLANIM ÖNERİLERİ:
1. Sık okunan, az güncellenen veriler için ideal
2. Türetilen metrikleri cache olarak sakla
3. Aggregation pipeline'ları kullan
4. Index'leri doğru tanımla
5. Embedded documents ile join'leri azalt
*/
