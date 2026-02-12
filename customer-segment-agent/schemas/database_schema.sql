-- ============================================================================
-- Çoklu Ajan Kampanya Zekası Sistemi - Veritabanı Şeması
-- Multi-Tenant Mimari
-- ============================================================================

-- ============================================================================
-- 1. TENANT YÖNETİMİ
-- ============================================================================

CREATE TABLE tenants (
    tenant_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    api_key VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Tenant ayarları
    margin_floor DECIMAL(5,2) DEFAULT 25.00,
    stock_days_threshold INT DEFAULT 60,
    max_recommendations INT DEFAULT 3,
    currency VARCHAR(3) DEFAULT 'TRY',
  

    INDEX idx_tenant_active (is_active),
    INDEX idx_tenant_created (created_at)
);

-- ============================================================================
-- 2. BÖLGE VE İKLİM YÖNETİMİ (Paylaşımlı - Tüm Tenant'lar İçin)
-- ============================================================================

CREATE TABLE regions (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    climate_type VARCHAR(50) NOT NULL,
    median_basket DECIMAL(10,2) NOT NULL,
    trend VARCHAR(50) NOT NULL,
    
    INDEX idx_region_name (name),
    INDEX idx_climate_type (climate_type)
);

CREATE TABLE cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    region_id INT NOT NULL,
    
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE CASCADE,
    INDEX idx_city_name (city_name),
    INDEX idx_region (region_id)
);

CREATE TABLE seasonal_needs (
    seasonal_need_id INT AUTO_INCREMENT PRIMARY KEY,
    region_id INT NOT NULL,
    season ENUM('winter', 'summer', 'spring', 'autumn') NOT NULL,
    need_tag VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE CASCADE,
    INDEX idx_region_season (region_id, season),
    INDEX idx_need_tag (need_tag)
);

-- ============================================================================
-- 3. ÜRÜN YÖNETİMİ (Tenant Bazlı)
-- ============================================================================

CREATE TABLE products (
    product_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category ENUM('MAKEUP', 'SKINCARE', 'FRAGRANCE', 'PERSONALCARE', 'HAIRCARE', 'WELLNESS') NOT NULL,
    subcategory VARCHAR(100),
    season ENUM('all', 'winter', 'summer', 'spring', 'autumn') DEFAULT 'all',
    
    -- Stok bilgileri
    current_stock INT NOT NULL DEFAULT 0,
    last_30_days_sales INT NOT NULL DEFAULT 0,
    
    -- Fiyat bilgileri
    unit_cost DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    
    -- Kaynak bilgisi
    source_url VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (product_id, tenant_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    
    INDEX idx_tenant_category (tenant_id, category),
    INDEX idx_tenant_season (tenant_id, season),
    INDEX idx_stock_level (tenant_id, current_stock),
    INDEX idx_product_name (product_name)
);

CREATE TABLE product_tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    tag VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (product_id, tenant_id) REFERENCES products(product_id, tenant_id) ON DELETE CASCADE,
    INDEX idx_product (product_id, tenant_id),
    INDEX idx_tag (tag),
    INDEX idx_tenant_tag (tenant_id, tag)
);

-- ============================================================================
-- 4. MÜŞTERİ YÖNETİMİ (Tenant Bazlı)
-- ============================================================================

CREATE TABLE customers (
    customer_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    city_id INT NOT NULL,
    age INT,
    gender ENUM('F', 'M', 'U') DEFAULT 'U',
    registered_at DATE NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (customer_id, tenant_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    
    INDEX idx_tenant_city (tenant_id, city_id),
    INDEX idx_tenant_age (tenant_id, age),
    INDEX idx_tenant_gender (tenant_id, gender),
    INDEX idx_registered (registered_at)
);

-- ============================================================================
-- 5. ÜRÜN GEÇMİŞİ (Müşteri Alışveriş Özeti - Ürün Bazlı)
-- ============================================================================

CREATE TABLE product_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- Özet metrikler
    total_quantity INT NOT NULL DEFAULT 0,
    total_spent DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    order_count INT NOT NULL DEFAULT 0,
    
    -- Tarih bilgileri
    first_purchase DATE NOT NULL,
    last_purchase DATE NOT NULL,
    avg_days_between INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id, tenant_id) REFERENCES customers(customer_id, tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id, tenant_id) REFERENCES products(product_id, tenant_id) ON DELETE CASCADE,
    
    INDEX idx_customer (customer_id, tenant_id),
    INDEX idx_product (product_id, tenant_id),
    INDEX idx_category (category),
    INDEX idx_last_purchase (last_purchase),
    INDEX idx_tenant_customer_product (tenant_id, customer_id, product_id),
    
    UNIQUE KEY unique_customer_product (customer_id, tenant_id, product_id)
);

-- ============================================================================
-- 6. KATALOG KAYNAKLARI (Scraping Geçmişi)
-- ============================================================================

CREATE TABLE catalog_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    last_scraped TIMESTAMP,
    product_count INT DEFAULT 0,
    status ENUM('pending', 'success', 'failed') DEFAULT 'pending',
    error_message TEXT,
    
    -- CSS seçiciler (JSON formatında)
    selectors JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    INDEX idx_tenant (tenant_id),
    INDEX idx_url (url(255)),
    INDEX idx_last_scraped (last_scraped)
);

-- ============================================================================
-- 7. KAMPANYA YÖNETİMİ
-- ============================================================================

CREATE TABLE campaigns (
    campaign_id VARCHAR(100) PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50),
    city_id INT NOT NULL,
    
    -- Kampanya parametreleri
    objective ENUM('IncreaseRevenue', 'ClearOverstock', 'CustomerRetention') NOT NULL,
    event VARCHAR(100),
    
    -- Hedef segment
    target_churn_segment ENUM('Active', 'Warm', 'AtRisk'),
    target_value_segment ENUM('HighValue', 'Standard'),
    target_affinity VARCHAR(50),
    target_age_segment VARCHAR(50),
    
    -- Strateji
    strategy_type VARCHAR(100) NOT NULL,
    strategy_description TEXT,
    discount_percent DECIMAL(5,2),
    
    -- Mesajlaşma
    headline VARCHAR(255),
    subtext TEXT,
    event_theme VARCHAR(100),
    
    -- Metadata
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_version VARCHAR(20),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id, tenant_id) REFERENCES customers(customer_id, tenant_id) ON DELETE SET NULL,
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    
    INDEX idx_tenant (tenant_id),
    INDEX idx_customer (customer_id, tenant_id),
    INDEX idx_objective (objective),
    INDEX idx_generated (generated_at)
);

CREATE TABLE campaign_products (
    campaign_product_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    
    role ENUM('hero', 'anchor', 'bundled', 'clearance', 'complementary') NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    quantity INT DEFAULT 1,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id, tenant_id) REFERENCES products(product_id, tenant_id) ON DELETE CASCADE,
    
    INDEX idx_campaign (campaign_id),
    INDEX idx_product (product_id, tenant_id),
    INDEX idx_role (role)
);

CREATE TABLE campaign_recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    
    reason TEXT,
    match_score DECIMAL(5,2),
    
    -- Match faktörleri
    category_match DECIMAL(3,2),
    season_match DECIMAL(3,2),
    age_match DECIMAL(3,2),
    complementary_bonus DECIMAL(3,2),
    diversity_match DECIMAL(3,2),
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id, tenant_id) REFERENCES products(product_id, tenant_id) ON DELETE CASCADE,
    
    INDEX idx_campaign (campaign_id),
    INDEX idx_match_score (match_score DESC)
);

-- ============================================================================
-- 8. ANALİZ SONUÇLARI (Cache/Log Amaçlı)
-- ============================================================================

CREATE TABLE customer_insights (
    insight_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Segment bilgileri
    age_segment VARCHAR(50),
    churn_segment VARCHAR(20),
    value_segment VARCHAR(20),
    loyalty_tier VARCHAR(20),
    affinity_category VARCHAR(50),
    affinity_type VARCHAR(20),
    diversity_profile VARCHAR(20),
    
    -- Metrikler
    estimated_budget DECIMAL(10,2),
    avg_basket DECIMAL(10,2),
    avg_monthly_spend DECIMAL(10,2),
    last_purchase_days_ago INT,
    order_count INT,
    total_spent DECIMAL(10,2),
    membership_days INT,
    
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id, tenant_id) REFERENCES customers(customer_id, tenant_id) ON DELETE CASCADE,
    
    INDEX idx_customer (customer_id, tenant_id),
    INDEX idx_analyzed (analyzed_at),
    INDEX idx_segments (tenant_id, churn_segment, value_segment)
);

CREATE TABLE stock_insights (
    insight_id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    
    -- Stok metrikleri
    stock_days INT,
    daily_sales DECIMAL(10,2),
    inventory_pressure BOOLEAN DEFAULT FALSE,
    season_match BOOLEAN DEFAULT TRUE,
    
    -- Segment
    product_segment ENUM('Hero', 'Normal', 'SlowMover', 'DeadStock'),
    
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id, tenant_id) REFERENCES products(product_id, tenant_id) ON DELETE CASCADE,
    
    INDEX idx_product (product_id, tenant_id),
    INDEX idx_tenant (tenant_id),
    INDEX idx_segment (product_segment),
    INDEX idx_analyzed (analyzed_at)
);

-- ============================================================================
-- 9. VERİ İÇE AKTARMA GEÇMİŞİ
-- ============================================================================

CREATE TABLE import_history (
    import_id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    data_type ENUM('products', 'customers', 'catalog_scrape') NOT NULL,
    
    -- İstatistikler
    total_records INT DEFAULT 0,
    imported_records INT DEFAULT 0,
    skipped_records INT DEFAULT 0,
    error_records INT DEFAULT 0,
    
    -- Dosya bilgisi
    file_name VARCHAR(255),
    file_size_kb INT,
    
    -- Durum
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    error_log TEXT,
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    
    INDEX idx_tenant (tenant_id),
    INDEX idx_status (status),
    INDEX idx_started (started_at)
);

-- ============================================================================
-- 10. VIEWS (Sık Kullanılan Sorgular İçin)
-- ============================================================================

-- Müşteri özet görünümü
CREATE VIEW v_customer_summary AS
SELECT 
    c.customer_id,
    c.tenant_id,
    c.age,
    c.gender,
    c.registered_at,
    ci.city_name,
    r.name as region_name,
    r.climate_type,
    r.median_basket,
    COUNT(DISTINCT ph.product_id) as unique_products,
    SUM(ph.order_count) as total_orders,
    SUM(ph.total_spent) as total_spent,
    MAX(ph.last_purchase) as last_purchase_date,
    DATEDIFF(CURRENT_DATE, MAX(ph.last_purchase)) as days_since_last_purchase
FROM customers c
LEFT JOIN cities ci ON c.city_id = ci.city_id
LEFT JOIN regions r ON ci.region_id = r.region_id
LEFT JOIN product_history ph ON c.customer_id = ph.customer_id AND c.tenant_id = ph.tenant_id
GROUP BY c.customer_id, c.tenant_id, c.age, c.gender, c.registered_at, 
         ci.city_name, r.name, r.climate_type, r.median_basket;

-- Ürün stok durumu görünümü
CREATE VIEW v_product_stock_status AS
SELECT 
    p.product_id,
    p.tenant_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.current_stock,
    p.last_30_days_sales,
    ROUND(p.last_30_days_sales / 30, 2) as daily_sales,
    CASE 
        WHEN p.last_30_days_sales = 0 THEN NULL
        ELSE ROUND(p.current_stock / (p.last_30_days_sales / 30), 0)
    END as stock_days,
    p.unit_cost,
    p.unit_price,
    ROUND(((p.unit_price - p.unit_cost) / p.unit_price) * 100, 2) as gross_margin_percent,
    CASE 
        WHEN p.last_30_days_sales = 0 AND p.current_stock > 0 THEN 'DeadStock'
        WHEN p.current_stock / (p.last_30_days_sales / 30) > 60 THEN 'SlowMover'
        WHEN p.current_stock / (p.last_30_days_sales / 30) <= 20 THEN 'Hero'
        ELSE 'Normal'
    END as stock_segment
FROM products p;

-- Kampanya performans özeti
CREATE VIEW v_campaign_summary AS
SELECT 
    c.campaign_id,
    c.tenant_id,
    c.objective,
    c.event,
    ci.city_name,
    r.name as region_name,
    c.strategy_type,
    c.discount_percent,
    COUNT(DISTINCT cp.product_id) as product_count,
    COUNT(DISTINCT CASE WHEN cp.role = 'hero' THEN cp.product_id END) as hero_count,
    COUNT(DISTINCT CASE WHEN cp.role = 'clearance' THEN cp.product_id END) as clearance_count,
    COUNT(DISTINCT cr.product_id) as recommendation_count,
    c.generated_at
FROM campaigns c
LEFT JOIN cities ci ON c.city_id = ci.city_id
LEFT JOIN regions r ON ci.region_id = r.region_id
LEFT JOIN campaign_products cp ON c.campaign_id = cp.campaign_id
LEFT JOIN campaign_recommendations cr ON c.campaign_id = cr.campaign_id
GROUP BY c.campaign_id, c.tenant_id, c.objective, c.event, ci.city_name, 
         r.name, c.strategy_type, c.discount_percent, c.generated_at;

-- ============================================================================
-- 11. STORED PROCEDURES (Sık Kullanılan İşlemler)
-- ============================================================================

DELIMITER //

-- Müşteri segmentasyonu hesaplama
CREATE PROCEDURE sp_calculate_customer_segment(
    IN p_customer_id VARCHAR(50),
    IN p_tenant_id VARCHAR(50)
)
BEGIN
    DECLARE v_days_since_last INT;
    DECLARE v_avg_basket DECIMAL(10,2);
    DECLARE v_median_basket DECIMAL(10,2);
    DECLARE v_membership_days INT;
    DECLARE v_order_count INT;
    DECLARE v_churn_segment VARCHAR(20);
    DECLARE v_value_segment VARCHAR(20);
    
    -- Metrikleri hesapla
    SELECT 
        DATEDIFF(CURRENT_DATE, MAX(ph.last_purchase)),
        SUM(ph.total_spent) / SUM(ph.order_count),
        r.median_basket,
        DATEDIFF(CURRENT_DATE, c.registered_at),
        SUM(ph.order_count)
    INTO 
        v_days_since_last,
        v_avg_basket,
        v_median_basket,
        v_membership_days,
        v_order_count
    FROM customers c
    LEFT JOIN cities ci ON c.city_id = ci.city_id
    LEFT JOIN regions r ON ci.region_id = r.region_id
    LEFT JOIN product_history ph ON c.customer_id = ph.customer_id AND c.tenant_id = ph.tenant_id
    WHERE c.customer_id = p_customer_id AND c.tenant_id = p_tenant_id
    GROUP BY c.customer_id, c.tenant_id, c.registered_at, r.median_basket;
    
    -- Churn segment
    IF v_days_since_last > 60 THEN
        SET v_churn_segment = 'AtRisk';
    ELSEIF v_days_since_last >= 30 THEN
        SET v_churn_segment = 'Warm';
    ELSE
        SET v_churn_segment = 'Active';
    END IF;
    
    -- Value segment
    IF v_avg_basket > v_median_basket THEN
        SET v_value_segment = 'HighValue';
    ELSE
        SET v_value_segment = 'Standard';
    END IF;
    
    SELECT v_churn_segment as churn_segment, v_value_segment as value_segment;
END //

DELIMITER ;

-- ============================================================================
-- 12. ÖRNEK VERİ EKLEME (Test Amaçlı)
-- ============================================================================

-- Tenant ekleme
INSERT INTO tenants (tenant_id, company_name, sector, contact_email, api_key) VALUES
('farmasi', 'Farmasi Türkiye', 'cosmetics', 'info@farmasi.com.tr', 'frm_a8f3d9c2b1e4f7a6');

-- Bölgeler
INSERT INTO regions (name, climate_type, median_basket, trend) VALUES
('Marmara', 'Metropol', 85.00, 'SKINCARE'),
('Ege', 'Sıcak-Nemli', 65.00, 'SKINCARE'),
('Akdeniz', 'Sıcak-Nemli', 60.00, 'MAKEUP'),
('İç Anadolu', 'Sıcak-Kuru', 55.00, 'SKINCARE'),
('Karadeniz', 'Soğuk', 50.00, 'SKINCARE'),
('Doğu Anadolu', 'Soğuk', 45.00, 'SKINCARE'),
('Güneydoğu Anadolu', 'Sıcak-Kuru', 50.00, 'FRAGRANCE');

-- Şehirler
INSERT INTO cities (city_name, region_id) VALUES
('Istanbul', 1), ('Bursa', 1), ('Kocaeli', 1),
('Izmir', 2), ('Mugla', 2), ('Aydin', 2),
('Antalya', 3), ('Mersin', 3), ('Adana', 3),
('Ankara', 4), ('Konya', 4), ('Kayseri', 4),
('Trabzon', 5), ('Samsun', 5), ('Rize', 5),
('Erzurum', 6), ('Van', 6), ('Kars', 6),
('Gaziantep', 7), ('Diyarbakir', 7), ('Sanliurfa', 7);

-- Mevsimsel ihtiyaçlar
INSERT INTO seasonal_needs (region_id, season, need_tag) VALUES
-- Marmara
(1, 'winter', 'nemlendirici'), (1, 'winter', 'dudak-bakım'), (1, 'winter', 'el-kremi'),
(1, 'summer', 'SPF'), (1, 'summer', 'hafif-nemlendirici'), (1, 'summer', 'mat-makyaj'),
-- Karadeniz
(5, 'winter', 'besleyici-krem'), (5, 'winter', 'dudak-bakım'), (5, 'winter', 'koruyucu-serum'), (5, 'winter', 'el-kremi'),
(5, 'summer', 'hafif-nemlendirici'), (5, 'summer', 'SPF');

-- ============================================================================
-- 13. İNDEKS OPTİMİZASYONU VE PERFORMANS
-- ============================================================================

-- Composite index'ler için analiz
ANALYZE TABLE customers, products, product_history, campaigns;

-- ============================================================================
-- NOTLAR
-- ============================================================================
-- 1. Multi-tenant izolasyon: Her tenant'ın verisi tenant_id ile ayrılır
-- 2. Bölge verileri paylaşımlıdır (regions, cities, seasonal_needs)
-- 3. product_history tablosu müşteri alışveriş özetini ürün bazında tutar
-- 4. Kampanya sonuçları ve öneriler ayrı tablolarda saklanır
-- 5. Views performans için sık kullanılan sorguları optimize eder
-- 6. JSON alanlar (selectors) esneklik sağlar
-- 7. Soft delete yerine hard delete kullanılır (CASCADE)
-- 8. Timestamp alanları otomatik güncellenir
-- 9. ENUM'lar veri tutarlılığını sağlar
-- 10. Foreign key'ler referans bütünlüğünü korur
