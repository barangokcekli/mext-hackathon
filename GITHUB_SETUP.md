# GitHub'a Yükleme Rehberi

## 🚨 ÖNEMLİ: Hassas Bilgileri Temizleme

GitHub'a yüklemeden ÖNCE mutlaka yapılması gerekenler:

### 1. Hassas Dosyaları Kontrol Et

```bash
# Bu dosyalar ASLA commit edilmemeli:
# - credits.txt (AWS credentials içeriyor!)
# - .bedrock_agentcore.yaml (deployment bilgileri)
# - .aws/ klasörü
```

### 2. .gitignore Dosyasını Kontrol Et

`.gitignore` dosyası zaten oluşturuldu ve şunları içeriyor:
- AWS credentials
- Virtual environment
- Python cache dosyaları
- IDE ayarları
- Log dosyaları

### 3. Hassas Bilgileri Temizle

```bash
# Eğer daha önce commit ettiyseniz, git history'den silin:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch credits.txt" \
  --prune-empty --tag-name-filter cat -- --all

# Veya daha modern yöntem (git-filter-repo):
git filter-repo --path credits.txt --invert-paths
```

## 📋 Adım Adım GitHub'a Yükleme

### Adım 1: Git Repository Başlat

```bash
# Eğer henüz git init yapmadıysanız:
git init

# .gitignore'u ekle
git add .gitignore

# İlk commit
git commit -m "Initial commit: Add .gitignore"
```

### Adım 2: Dosyaları Ekle

```bash
# Tüm dosyaları ekle (hassas dosyalar .gitignore'da olduğu için eklenmeyecek)
git add .

# Commit et
git commit -m "Add Customer Segment Agent implementation"
```

### Adım 3: GitHub Repository Oluştur

1. GitHub'da yeni repository oluştur: https://github.com/new
2. Repository adı: `customer-segment-agent`
3. Description: "AI-powered customer segmentation agent on AWS Bedrock AgentCore"
4. Public veya Private seç (önerim: Private, çünkü AWS bilgileri var)
5. README, .gitignore, license ekleme (zaten var)

### Adım 4: Remote Ekle ve Push Et

```bash
# GitHub repository'nizi remote olarak ekleyin
git remote add origin https://github.com/YOUR_USERNAME/customer-segment-agent.git

# Main branch'i push edin
git branch -M main
git push -u origin main
```

## 🔒 Güvenlik Kontrol Listesi

Push etmeden önce kontrol edin:

- [ ] `credits.txt` dosyası commit edilmemiş
- [ ] `.bedrock_agentcore.yaml` commit edilmemiş
- [ ] `.aws/` klasörü commit edilmemiş
- [ ] `.gitignore` dosyası doğru yapılandırılmış
- [ ] README.md'de gerçek AWS ARN'ler var mı? (Varsa placeholder'a çevir)
- [ ] DEPLOYMENT_INFO.md'de hassas bilgi var mı? (Account ID, ARN'ler)

## 📝 Hassas Bilgileri Placeholder'a Çevirme

Eğer dokümanlarda gerçek AWS bilgileri varsa, placeholder'a çevirin:

```bash
# Örnek: DEPLOYMENT_INFO.md'deki gerçek ARN'leri değiştir
sed -i 's/485169707250/YOUR_AWS_ACCOUNT_ID/g' DEPLOYMENT_INFO.md
sed -i 's/customer_segment_agent-1GD3a24jRt/customer_segment_agent-XXXXX/g' DEPLOYMENT_INFO.md
```

## 🌟 Repository Ayarları (GitHub'da)

### 1. Branch Protection

Settings → Branches → Add rule:
- Branch name pattern: `main`
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging

### 2. Secrets (CI/CD için)

Settings → Secrets and variables → Actions:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: us-west-2

### 3. Topics (Keşfedilebilirlik için)

Repository ana sayfasında "Add topics":
- `aws`
- `bedrock`
- `agentcore`
- `customer-segmentation`
- `ai-agent`
- `strands-agents`
- `python`

## 📄 README Badge'leri Güncelle

README.md'deki badge'leri kendi repository'nize göre güncelleyin:

```markdown
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20AgentCore-orange)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/github/stars/YOUR_USERNAME/customer-segment-agent?style=social)](https://github.com/YOUR_USERNAME/customer-segment-agent)
```

## 🔄 Sürekli Güncelleme

### Yeni Değişiklikler Eklemek

```bash
# Değişiklikleri stage'e al
git add .

# Commit et
git commit -m "feat: Add new feature"

# Push et
git push origin main
```

### Commit Message Formatı

Conventional Commits kullanın:
- `feat:` Yeni özellik
- `fix:` Bug fix
- `docs:` Dokümantasyon değişikliği
- `refactor:` Kod refactoring
- `test:` Test ekleme/güncelleme
- `chore:` Bakım işleri

## 📦 Release Oluşturma

```bash
# Tag oluştur
git tag -a v1.0.0 -m "Release version 1.0.0"

# Tag'i push et
git push origin v1.0.0
```

GitHub'da Releases → Create a new release:
- Tag: v1.0.0
- Title: "Customer Segment Agent v1.0.0"
- Description: Release notes

## 🤝 Collaboration

### Pull Request Template

`.github/pull_request_template.md` oluşturun:

```markdown
## Description
<!-- Değişikliklerinizi açıklayın -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No sensitive data included
```

### Issue Template

`.github/ISSUE_TEMPLATE/bug_report.md` oluşturun:

```markdown
---
name: Bug Report
about: Report a bug
title: '[BUG] '
labels: bug
---

## Description
<!-- Bug'ı açıklayın -->

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior
<!-- Ne olmasını bekliyordunuz? -->

## Actual Behavior
<!-- Ne oldu? -->

## Environment
- OS: 
- Python Version: 
- AWS Region: 
```

## 🎯 Sonraki Adımlar

1. ✅ Repository'yi oluştur
2. ✅ Hassas bilgileri temizle
3. ✅ Push et
4. ✅ README'yi güncelle
5. ✅ Branch protection ekle
6. ✅ Topics ekle
7. ✅ License ekle (MIT önerilir)
8. ✅ Contributing guidelines ekle
9. ✅ Code of conduct ekle
10. ✅ GitHub Actions CI/CD ekle (opsiyonel)

## 🚀 Hızlı Komutlar

```bash
# Tüm işlemi tek seferde:
git init
git add .
git commit -m "Initial commit: Customer Segment Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/customer-segment-agent.git
git push -u origin main
```

## ⚠️ Son Kontrol

Push etmeden önce:

```bash
# Hangi dosyaların commit edileceğini kontrol et
git status

# Hassas dosya var mı kontrol et
git ls-files | grep -E "(credits|\.aws|\.env)"

# Eğer çıktı varsa, bu dosyaları .gitignore'a ekle ve:
git rm --cached <filename>
git commit -m "Remove sensitive file"
```

## 📞 Yardım

Sorun yaşarsanız:
1. `.gitignore` dosyasını kontrol edin
2. `git status` ile hangi dosyaların tracked olduğunu görün
3. Hassas dosyaları `git rm --cached` ile kaldırın
4. Gerekirse git history'yi temizleyin

---

**Önemli**: GitHub'a push ettikten sonra, `credits.txt` dosyasını asla commit etmeyin. Eğer yanlışlıkla commit ederseniz, hemen repository'yi private yapın ve git history'yi temizleyin!
