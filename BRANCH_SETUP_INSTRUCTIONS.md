# Branch Setup Instructions for barangokcekli

## 🎯 Durum

Customer Segment Agent kodu şu anda `7Auri/mext-hackathon` fork'unda `feature/customer-segment-agent` branch'inde.

## 📋 Barangokcekli İçin Talimatlar

Kendi repo'nuzda (barangokcekli/mext-hackathon) yeni bir branch oluşturup kodu oraya çekmek için:

### Yöntem 1: GitHub Web Interface (En Kolay)

1. PR'ı kabul et: https://github.com/barangokcekli/mext-hackathon/pull/2
2. "Merge pull request" yerine "Create a merge commit" seç
3. Veya "Squash and merge" kullan
4. Branch otomatik olarak oluşturulur

### Yöntem 2: Git CLI ile

```bash
# 1. Repo'yu klonla (eğer yoksa)
git clone https://github.com/barangokcekli/mext-hackathon.git
cd mext-hackathon

# 2. 7Auri'nin fork'unu remote olarak ekle
git remote add auri https://github.com/7Auri/mext-hackathon.git

# 3. Remote'ları fetch et
git fetch auri

# 4. Yeni branch oluştur ve 7Auri'nin branch'ini çek
git checkout -b feature/customer-segment-agent auri/feature/customer-segment-agent

# 5. Kendi repo'na push et
git push origin feature/customer-segment-agent
```

### Yöntem 3: GitHub CLI ile

```bash
# PR'ı checkout et
gh pr checkout 2 --repo barangokcekli/mext-hackathon

# Yeni branch oluştur
git checkout -b feature/customer-segment-agent

# Push et
git push origin feature/customer-segment-agent
```

## 🎯 Sonuç

Bu işlemlerden sonra `barangokcekli/mext-hackathon` repo'sunda `feature/customer-segment-agent` branch'i oluşacak ve tüm kod orada olacak.

## 📦 Branch İçeriği

- customer_segment_agent.py
- customer-segment-agent-api.md
- INTEGRATION_GUIDE.md
- REMOTE_ACCESS_GUIDE.md
- DEPLOYMENT_INFO.md
- mock-data/
- .kiro/specs/
- Ve diğer tüm dosyalar (34 dosya, 11,954+ satır)

## 🔗 Linkler

- **PR**: https://github.com/barangokcekli/mext-hackathon/pull/2
- **Source Branch**: https://github.com/7Auri/mext-hackathon/tree/feature/customer-segment-agent
- **Target Repo**: https://github.com/barangokcekli/mext-hackathon

---

**Not**: Branch şu anda 7Auri'nin fork'unda. Yukarıdaki yöntemlerden biriyle kendi repo'nuza çekebilirsiniz.
