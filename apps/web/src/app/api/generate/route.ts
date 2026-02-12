import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { prompt, files, campaignTitle } = await request.json();

  if (!prompt) {
    return NextResponse.json({ error: "Prompt gerekli" }, { status: 400 });
  }

  // Simulate AI processing
  await new Promise((resolve) => setTimeout(resolve, 3000));

  const fileContext = files?.length
    ? `\n\n📎 ${files.length} dosya analiz edildi: ${files.map((f: { name: string }) => f.name).join(", ")}`
    : "";

  const campaignContext = campaignTitle
    ? `"${campaignTitle}" kampanyası için `
    : "";

  const result = `${campaignContext}AI tarafından oluşturulan kampanya içeriği:

📋 Kampanya Özeti
${prompt.slice(0, 100)}... talimatınıza göre aşağıdaki strateji önerilmektedir.

🎯 Hedef Kitle
- 25-45 yaş arası dijital alışveriş yapan kullanıcılar
- Daha önce benzer ürünlere ilgi göstermiş segmentler
- Yüksek etkileşim potansiyeli olan sosyal medya kullanıcıları

📝 İçerik Planı
1. Dikkat çekici başlık ve görsel tasarım
2. Kişiselleştirilmiş mesaj içerikleri
3. A/B test senaryoları
4. Zamanlama ve frekans optimizasyonu

📊 Beklenen Sonuçlar
- Tahmini erişim: 25.000+ kişi
- Beklenen dönüşüm oranı: %3.5
- ROI tahmini: 4.2x${fileContext}

⚠️ Bu bir demo çıktısıdır. Gerçek AI entegrasyonu ile çok daha detaylı sonuçlar alınacaktır.`;

  return NextResponse.json({ result });
}
