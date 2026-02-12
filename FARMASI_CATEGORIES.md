# Farmasi Ürün Kategori Yapısı

farmasi.com.tr ve üçüncü parti kaynaklardan derlenen Farmasi ürün ağacı.
Bu yapı `products.json` veri modelinin category/subcategory/tags alanlarını belirler.

> Not: farmasi.com.tr tamamen client-side JS ile render edildiği için doğrudan scrape edilemedi.
> Kategori yapısı Farmasi US, Farmasi MY, reseller siteleri ve ürün inceleme kaynaklarından derlenmiştir.

---

## 1. Ana Kategoriler

| # | Kategori | Kod | Açıklama |
|---|---|---|---|
| 1 | Makyaj | MAKEUP | Renkli kozmetik, yüz, göz, dudak, tırnak |
| 2 | Cilt Bakımı | SKINCARE | Yüz bakım, temizleme, nemlendirme, anti-aging |
| 3 | Parfüm & Koku | FRAGRANCE | Kadın, erkek, unisex parfümler, vücut spreyleri |
| 4 | Kişisel Bakım | PERSONALCARE | Ağız bakım, deodorant, duş, vücut bakım |
| 5 | Saç Bakımı | HAIRCARE | Şampuan, saç kremi, maske, saç şekillendirme |
| 6 | Sağlık & Wellness | WELLNESS | Takviye gıda, vitamin, kolajen, bitkisel ürünler |

---

## 2. Alt Kategoriler ve Örnek Ürünler

### 2.1 MAKEUP — Makyaj

| Alt Kategori | Örnek Ürünler | Etiketler (tags) |
|---|---|---|
| Fondöten | VFX Pro Camera Ready Foundation, CC Cream, BB Cream | fondöten, baz, kapatıcı, mat, doğal |
| Pudra | Terracotta Porcelain Powder, Translucent Powder | pudra, mat, aydınlatıcı |
| Kapatıcı & Kontür | Concealer Palette, Contour Kit | kapatıcı, kontür, aydınlatıcı |
| Primer | VFX Pro Makeup Primer | primer, baz, gözenek |
| Allık & Bronzer | Tender Blush, Bronzing Powder | allık, bronzer, aydınlatıcı |
| Maskara | Full Blast Mascara, Extreme Curl False Lash Effect | maskara, hacim, uzatıcı, kıvırıcı |
| Eyeliner | Styler Eyeliner Pen, Kajal Eyeliner | eyeliner, kalem, likit |
| Far | Long Lasting Creamy Eyeshadow, Eyeshadow Palette | far, palet, simli, mat |
| Kaş | Brow Pencil, Brow Gel | kaş, şekillendirici |
| Ruj & Dudak | Stay Matte Liquid Lipstick, Lip Gloss, Lip Pencil, Latina Lip Lacquer | ruj, dudak, mat, parlak, kalem |
| Tırnak | Nail Color, Nail Care | oje, tırnak, bakım |
| Makyaj Aksesuarları | Fırça Seti, Makyaj Süngeri | fırça, sünger, aksesuar |

### 2.2 SKINCARE — Cilt Bakımı

| Alt Kategori | Örnek Ürünler | Etiketler |
|---|---|---|
| Yüz Temizleme | Dr. C. Tuna Tea Tree Face Wash, Cleansing Balm, Micellar Water | temizleyici, jel, köpük, misel, makyaj-temizleme |
| Tonik & Sprey | Dr. C. Tuna Pure Rose Toner Spray | tonik, sprey, canlandırıcı |
| Serum | Dr. C. Tuna Tea Tree SOS Serum, Age Reversist Serum | serum, anti-aging, leke, aydınlatıcı, akne |
| Nemlendirici | Aloe Line Moisturizer, Hyaluronic Acid Cream | nemlendirici, hafif, yoğun, hyaluronik |
| Anti-Aging | Age Reversist Line, Peptide Complex | anti-aging, kırışıklık, sıkılaştırıcı |
| Güneş Koruma | Dr. C. Tuna Sun Face Cream, Sun Body Lotion | SPF, güneş, koruma, bronzlaştırıcı |
| Maske & Peeling | Charcoal Mask, Peeling Gel | maske, peeling, arındırıcı, detox |
| Göz Bakımı | Eye Contour Cream | göz, koyu-halka, şişlik |
| Dudak Bakımı | Lip Balm, Lip Scrub | dudak-bakım, nemlendirici |
| Özel Bakım | Acne Set, Calendula Line | akne, hassas-cilt, onarıcı |

### 2.3 FRAGRANCE — Parfüm & Koku

| Alt Kategori | Örnek Ürünler | Etiketler |
|---|---|---|
| Kadın Parfüm | Hera, Bouquet, Donna | kadın, çiçeksi, oryantal, tatlı |
| Erkek Parfüm | Mr. Clever, Shooter's, Uomo | erkek, odunsu, aromatik, taze |
| Unisex Parfüm | — | unisex, modern |
| Vücut Spreyi | Body Mist serisi | sprey, hafif, günlük |
| Kolonya | — | kolonya, ferahlatıcı |

### 2.4 PERSONALCARE — Kişisel Bakım

| Alt Kategori | Örnek Ürünler | Etiketler |
|---|---|---|
| Ağız Bakımı | Eurofresh Whitening Toothpaste (Saffron & Matcha), Mouthwash | diş-macunu, ağız-bakım, beyazlatıcı |
| Duş & Banyo | Papaya Body Wash, Shower Gel | duş-jeli, banyo, temizleyici |
| Sabun | Dr. C. Tuna Calendula Soap, Shea Butter Soap | sabun, katı, doğal |
| Deodorant | Roll-on, Spray Deodorant | deodorant, ter-önleyici |
| Vücut Bakımı | Aloe Glow Lotion, Calendula Hand Cream, Shea & Almond Line | vücut-losyonu, el-kremi, nemlendirici, besleyici |
| El & Ayak Bakımı | Hand Cream, Foot Cream | el-kremi, ayak-bakım |
| Tıraş & Erkek Bakım | Shaving Gel, Aftershave, Men's Grooming Set | tıraş, aftershave, erkek-bakım |
| Islak Mendil | Baby Wipes, Makeup Remover Wipes | ıslak-mendil, temizleyici |

### 2.5 HAIRCARE — Saç Bakımı

| Alt Kategori | Örnek Ürünler | Etiketler |
|---|---|---|
| Şampuan | Dr. C. Tuna Hydrating Shampoo, Keratin Therapy Shampoo | şampuan, nemlendirici, onarıcı, keratin |
| Saç Kremi | Keratin Therapy Conditioner | saç-kremi, yumuşatıcı |
| Saç Maskesi | Dr. C. Tuna Intensive Repair Hair Mask | maske, onarıcı, besleyici |
| Saç Yağı & Serum | Reviving Hair Oil Elixir | saç-yağı, serum, parlaklık |
| Saç Şekillendirme | Hair Spray, Styling Gel | şekillendirici, sprey, jöle |

### 2.6 WELLNESS — Sağlık & Wellness

| Alt Kategori | Örnek Ürünler | Etiketler |
|---|---|---|
| Takviye & Vitamin | Nutriplus Vitamin serisi, Multivitamin | vitamin, takviye, bağışıklık |
| Kolajen | Beauty Booster Collagen (Chocolate) | kolajen, güzellik, eklem |
| Enerji & Metabolizma | L-Carnitine Shots, Farmasi Coffee with Chicory | enerji, metabolizma, kahve |
| Sindirim & Bağırsak | Apple Cider Gummies | sindirim, probiyotik, bağırsak |
| Bitkisel Ürünler | Dr. C. Tuna Massage Gel (Horse Chestnut Balsam) | bitkisel, masaj, rahatlatıcı |
| Çay & İçecek | Herbal Tea serisi | çay, bitkisel, detox |

---

## 3. Ürün-Etiket Eşleme Kuralları (Sistem İçin)

Ürün etiketleri, bölge iklim tipi ve mevsimsel ihtiyaçlarla eşleştirilir:

| Mevsim + İklim | Öncelikli Etiketler |
|---|---|
| Kış + Soğuk | besleyici, yoğun, nemlendirici, dudak-bakım, el-kremi, koruyucu, onarıcı |
| Kış + Sıcak-Kuru | yoğun-nemlendirici, koruyucu, bariyer, dudak-bakım |
| Yaz + Sıcak-Nemli | SPF, güneş, hafif, mat, bronzlaştırıcı, hafif-nemlendirici |
| Yaz + Metropol | SPF, hafif, trend, mat, bronzlaştırıcı |
| İlkbahar | temizleyici, serum, anti-aging, tonik, canlandırıcı |
| Sonbahar | onarıcı, besleyici, maske, nemlendirici |

| Yaş Segmenti | Öncelikli Etiketler |
|---|---|
| GenZ (18-25) | trend, mat, renkli, oje, dudak, maskara, hafif |
| Genç Yetişkin (26-35) | serum, anti-aging, nemlendirici, SPF, temizleyici |
| Yetişkin (36-50) | anti-aging, kırışıklık, sıkılaştırıcı, premium, parfüm |
| Olgun (51+) | anti-aging, besleyici, onarıcı, kolajen, vitamin |

| Cinsiyet | Öncelikli Etiketler |
|---|---|
| F | tam erişim |
| M | erkek-bakım, tıraş, aftershave, parfüm (erkek), şampuan, deodorant |
| null | unisex, nötr etiketli ürünler |

---

## 4. products.json Güncellenmiş Örnek Kayıtlar

```json
[
  {
    "productId": "P-1001",
    "productName": "VFX Pro Camera Ready Foundation",
    "category": "MAKEUP",
    "subcategory": "Fondöten",
    "tags": ["fondöten", "mat", "doğal", "trend"],
    "season": "all",
    "currentStock": 850,
    "last30DaysSales": 120,
    "unitCost": 35.00,
    "unitPrice": 89.90
  },
  {
    "productId": "P-1002",
    "productName": "Full Blast Mascara",
    "category": "MAKEUP",
    "subcategory": "Maskara",
    "tags": ["maskara", "hacim", "uzatıcı", "trend"],
    "season": "all",
    "currentStock": 1200,
    "last30DaysSales": 200,
    "unitCost": 18.00,
    "unitPrice": 54.90
  },
  {
    "productId": "P-1003",
    "productName": "Stay Matte Liquid Lipstick",
    "category": "MAKEUP",
    "subcategory": "Ruj & Dudak",
    "tags": ["ruj", "mat", "dudak", "trend", "renkli"],
    "season": "all",
    "currentStock": 600,
    "last30DaysSales": 85,
    "unitCost": 15.00,
    "unitPrice": 44.90
  },
  {
    "productId": "P-2001",
    "productName": "Dr. C. Tuna Tea Tree Face Wash",
    "category": "SKINCARE",
    "subcategory": "Yüz Temizleme",
    "tags": ["temizleyici", "jel", "akne", "arındırıcı"],
    "season": "all",
    "currentStock": 900,
    "last30DaysSales": 75,
    "unitCost": 20.00,
    "unitPrice": 59.90
  },
  {
    "productId": "P-2002",
    "productName": "Age Reversist Serum",
    "category": "SKINCARE",
    "subcategory": "Serum",
    "tags": ["serum", "anti-aging", "kırışıklık", "aydınlatıcı"],
    "season": "all",
    "currentStock": 400,
    "last30DaysSales": 60,
    "unitCost": 40.00,
    "unitPrice": 119.90
  },
  {
    "productId": "P-2003",
    "productName": "Dr. C. Tuna Sun Face Cream SPF50",
    "category": "SKINCARE",
    "subcategory": "Güneş Koruma",
    "tags": ["SPF", "güneş", "koruma", "hafif"],
    "season": "summer",
    "currentStock": 1500,
    "last30DaysSales": 30,
    "unitCost": 25.00,
    "unitPrice": 74.90
  },
  {
    "productId": "P-2004",
    "productName": "Aloe Line Moisturizer",
    "category": "SKINCARE",
    "subcategory": "Nemlendirici",
    "tags": ["nemlendirici", "hafif", "aloe", "canlandırıcı"],
    "season": "all",
    "currentStock": 700,
    "last30DaysSales": 95,
    "unitCost": 22.00,
    "unitPrice": 64.90
  },
  {
    "productId": "P-2005",
    "productName": "Charcoal Mask",
    "category": "SKINCARE",
    "subcategory": "Maske & Peeling",
    "tags": ["maske", "detox", "arındırıcı", "gözenek"],
    "season": "all",
    "currentStock": 500,
    "last30DaysSales": 40,
    "unitCost": 18.00,
    "unitPrice": 49.90
  },
  {
    "productId": "P-2006",
    "productName": "Dr. C. Tuna Intensive Moisturizing Cream",
    "category": "SKINCARE",
    "subcategory": "Nemlendirici",
    "tags": ["nemlendirici", "yoğun", "besleyici", "koruyucu", "bariyer"],
    "season": "winter",
    "currentStock": 800,
    "last30DaysSales": 45,
    "unitCost": 28.00,
    "unitPrice": 79.90
  },
  {
    "productId": "P-3001",
    "productName": "Hera EDP Kadın Parfüm",
    "category": "FRAGRANCE",
    "subcategory": "Kadın Parfüm",
    "tags": ["kadın", "çiçeksi", "oryantal", "parfüm"],
    "season": "all",
    "currentStock": 350,
    "last30DaysSales": 55,
    "unitCost": 45.00,
    "unitPrice": 149.90
  },
  {
    "productId": "P-3002",
    "productName": "Mr. Clever EDP Erkek Parfüm",
    "category": "FRAGRANCE",
    "subcategory": "Erkek Parfüm",
    "tags": ["erkek", "odunsu", "aromatik", "parfüm", "erkek-bakım"],
    "season": "all",
    "currentStock": 280,
    "last30DaysSales": 40,
    "unitCost": 42.00,
    "unitPrice": 139.90
  },
  {
    "productId": "P-4001",
    "productName": "Eurofresh Whitening Toothpaste",
    "category": "PERSONALCARE",
    "subcategory": "Ağız Bakımı",
    "tags": ["diş-macunu", "beyazlatıcı", "ağız-bakım"],
    "season": "all",
    "currentStock": 2000,
    "last30DaysSales": 300,
    "unitCost": 8.00,
    "unitPrice": 29.90
  },
  {
    "productId": "P-4002",
    "productName": "Calendula Hand Cream",
    "category": "PERSONALCARE",
    "subcategory": "El & Ayak Bakımı",
    "tags": ["el-kremi", "nemlendirici", "besleyici", "onarıcı"],
    "season": "winter",
    "currentStock": 600,
    "last30DaysSales": 50,
    "unitCost": 12.00,
    "unitPrice": 34.90
  },
  {
    "productId": "P-4003",
    "productName": "Aloe Glow Body Lotion",
    "category": "PERSONALCARE",
    "subcategory": "Vücut Bakımı",
    "tags": ["vücut-losyonu", "hafif", "nemlendirici", "aloe"],
    "season": "all",
    "currentStock": 450,
    "last30DaysSales": 65,
    "unitCost": 20.00,
    "unitPrice": 59.90
  },
  {
    "productId": "P-5001",
    "productName": "Keratin Therapy Shampoo",
    "category": "HAIRCARE",
    "subcategory": "Şampuan",
    "tags": ["şampuan", "onarıcı", "keratin", "parlaklık"],
    "season": "all",
    "currentStock": 700,
    "last30DaysSales": 80,
    "unitCost": 18.00,
    "unitPrice": 49.90
  },
  {
    "productId": "P-5002",
    "productName": "Dr. C. Tuna Intensive Repair Hair Mask",
    "category": "HAIRCARE",
    "subcategory": "Saç Maskesi",
    "tags": ["maske", "onarıcı", "besleyici", "keratin"],
    "season": "all",
    "currentStock": 350,
    "last30DaysSales": 35,
    "unitCost": 22.00,
    "unitPrice": 64.90
  },
  {
    "productId": "P-6001",
    "productName": "Beauty Booster Collagen Chocolate",
    "category": "WELLNESS",
    "subcategory": "Kolajen",
    "tags": ["kolajen", "güzellik", "anti-aging", "takviye"],
    "season": "all",
    "currentStock": 200,
    "last30DaysSales": 25,
    "unitCost": 55.00,
    "unitPrice": 179.90
  },
  {
    "productId": "P-6002",
    "productName": "L-Carnitine Energy Shot",
    "category": "WELLNESS",
    "subcategory": "Enerji & Metabolizma",
    "tags": ["enerji", "metabolizma", "takviye", "spor"],
    "season": "all",
    "currentStock": 500,
    "last30DaysSales": 70,
    "unitCost": 10.00,
    "unitPrice": 34.90
  },
  {
    "productId": "P-2007",
    "productName": "Dr. C. Tuna Lip Balm",
    "category": "SKINCARE",
    "subcategory": "Dudak Bakımı",
    "tags": ["dudak-bakım", "nemlendirici", "koruyucu", "besleyici"],
    "season": "winter",
    "currentStock": 1100,
    "last30DaysSales": 55,
    "unitCost": 8.00,
    "unitPrice": 24.90
  }
]
```

---

## 5. DB_SCHEMA.md ile Uyum

`products.json` şeması güncellendi:

| Alan | Eski | Yeni |
|---|---|---|
| category | "Skincare" / "Perfume" / "Makeup" | "MAKEUP" / "SKINCARE" / "FRAGRANCE" / "PERSONALCARE" / "HAIRCARE" / "WELLNESS" |
| subcategory | yoktu | Eklendi (Fondöten, Serum, Şampuan, vb.) |
| tags | genel etiketler | Farmasi ürün özelliklerine göre zenginleştirildi |
| season | "all" / "winter" / "summer" | Aynı, ürün bazında atandı |

`customers.json` içindeki `productHistory[]` elemanlarında `category` alanı artık 6 ana kategori kodundan birini alır.
