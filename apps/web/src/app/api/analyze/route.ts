import { NextRequest, NextResponse } from "next/server";
import type { Campaign } from "@/components/ui/CampaignCard";

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const { url } = await request.json();

  if (!url) {
    return NextResponse.json({ error: "URL gerekli" }, { status: 400 });
  }

  try {
    // Call orchestrator API
    const response = await fetch(`${ORCHESTRATOR_URL}/api/orchestrate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: `${url} için kampanya önerileri oluştur`,
        customerId: "C-2001", // Default customer
        maxProducts: 30,
        useLLM: false
      }),
    });

    if (!response.ok) {
      throw new Error("Orchestrator API error");
    }

    const data = await response.json();
    
    // Transform orchestrator response to Campaign format
    const campaigns: Campaign[] = data.campaigns.map((camp: any, index: number) => ({
      id: camp.campaignId || `camp-${index + 1}`,
      title: camp.title || "Kampanya",
      description: camp.description || "",
      type: "İndirim",
      channel: "Multi-Channel",
      estimatedReach: `${Math.round(camp.estimatedRevenue || 0)} TL`,
      difficulty: camp.discountRate > 30 ? "Kolay" : "Orta",
      products: camp.products || [],
      discountRate: camp.discountRate,
      targetSegment: camp.targetSegment,
      validUntil: camp.validUntil
    }));

    return NextResponse.json({ 
      campaigns, 
      analyzedUrl: url,
      orchestrationSummary: data.orchestrationSummary,
      customerInsight: data.customerInsight,
      productInsight: data.productInsight
    });
  } catch (error) {
    console.error("Orchestrator error:", error);
    
    // Fallback to mock data if orchestrator fails
    const mockCampaigns: Campaign[] = [
      {
        id: "1",
        title: "⚠️ Orchestrator'a bağlanılamadı",
        description: "Lütfen FastAPI server'ı başlatın:\n\ncd mext-hackathon && uvicorn api_server:app --host 0.0.0.0 --port 8000",
        type: "Hata",
        channel: "N/A",
        estimatedReach: "0",
        difficulty: "N/A",
      },
    ];

    return NextResponse.json({ campaigns: mockCampaigns, analyzedUrl: url });
  }
}
