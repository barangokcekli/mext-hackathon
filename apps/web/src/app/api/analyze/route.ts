import { NextRequest, NextResponse } from "next/server";
import type { Campaign } from "@/components/ui/CampaignCard";

const mockCampaigns: Campaign[] = [
  {
    id: "1",
    title: "Sezon Sonu İndirim E-posta Kampanyası",
    description: "Mevcut müşterilere özel sezon sonu indirimi ile ürün satışlarını artırın. Kişiselleştirilmiş e-posta içerikleri ile yüksek dönüşüm oranı.",
    type: "İndirim",
    channel: "E-posta",
    estimatedReach: "15.000+",
    difficulty: "Kolay",
  },
  {
    id: "2",
    title: "Instagram Reels Ürün Tanıtımı",
    description: "Kısa ve dikkat çekici Reels videoları ile ürününüzü geniş kitlelere tanıtın. Trend müzikler ve yaratıcı geçişlerle viral potansiyel.",
    type: "Tanıtım",
    channel: "Sosyal Medya",
    estimatedReach: "50.000+",
    difficulty: "Orta",
  },
  {
    id: "3",
    title: "Google Shopping Reklam Kampanyası",
    description: "Ürün araması yapan potansiyel müşterilere doğrudan ulaşın. Yüksek satın alma niyetli trafik ile ROI odaklı kampanya.",
    type: "Reklam",
    channel: "Google Ads",
    estimatedReach: "25.000+",
    difficulty: "Orta",
  },
  {
    id: "4",
    title: "Sadakat Programı SMS Bildirimi",
    description: "Sadık müşterilerinize özel fırsatları SMS ile anında iletin. Yüksek açılma oranı ile hızlı dönüşüm sağlayın.",
    type: "Sadakat",
    channel: "SMS",
    estimatedReach: "8.000+",
    difficulty: "Kolay",
  },
  {
    id: "5",
    title: "Mikro Influencer İş Birliği",
    description: "Niş alanınızdaki mikro influencer'lar ile organik ve güvenilir ürün tanıtımı yapın. Yüksek etkileşim oranı garantili.",
    type: "İş Birliği",
    channel: "Influencer",
    estimatedReach: "30.000+",
    difficulty: "Zor",
  },
  {
    id: "6",
    title: "Terk Edilen Sepet Kurtarma",
    description: "Sepetinde ürün bırakıp ayrılan ziyaretçilere otomatik push bildirim gönderin. Kaybedilen satışları geri kazanın.",
    type: "Retargeting",
    channel: "Push Bildirim",
    estimatedReach: "5.000+",
    difficulty: "Kolay",
  },
];

export async function POST(request: NextRequest) {
  const { url } = await request.json();

  if (!url) {
    return NextResponse.json({ error: "URL gerekli" }, { status: 400 });
  }

  // Simulate AI processing time
  await new Promise((resolve) => setTimeout(resolve, 7000));

  return NextResponse.json({ campaigns: mockCampaigns, analyzedUrl: url });
}
