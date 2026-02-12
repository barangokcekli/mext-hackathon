import { NextRequest, NextResponse } from "next/server";

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const { prompt, files, campaignTitle, customerId } = await request.json();

  if (!prompt) {
    return NextResponse.json({ error: "Prompt gerekli" }, { status: 400 });
  }

  // Dosya içeriklerini prompt'a ekle
  let fullPrompt = campaignTitle
    ? `"${campaignTitle}" kampanyası için: ${prompt}`
    : prompt;

  if (files?.length) {
    const fileContents = files
      .map((f: { name: string; content: string }) => `--- ${f.name} ---\n${f.content}`)
      .join("\n\n");
    fullPrompt += `\n\nEklenen dosyalar:\n${fileContents}`;
  }

  try {
    const res = await fetch(`${ORCHESTRATOR_URL}/api/orchestrate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: fullPrompt,
        customerId: customerId || null,
        useLLM: true,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return NextResponse.json(
        { error: err.detail || "Orchestrator hatası", result: formatError(err) },
        { status: res.status }
      );
    }

    const data = await res.json();

    // Frontend'in beklediği formata dönüştür
    const result = formatResult(data, campaignTitle);
    return NextResponse.json({ result, raw: data });
  } catch (error) {
    // FastAPI'ye ulaşılamıyorsa fallback
    console.error("Orchestrator bağlantı hatası:", error);
    return NextResponse.json({
      error: "Orchestrator'a bağlanılamadı. FastAPI server çalışıyor mu?",
      result: `⚠️ Orchestrator'a bağlanılamadı.\n\nLütfen FastAPI server'ı başlatın:\n  cd mext-hackathon && uvicorn api_server:app --host 0.0.0.0 --port 8000\n\nPrompt: ${fullPrompt}`,
    });
  }
}

function formatResult(data: Record<string, unknown>, campaignTitle?: string): string {
  const ci = data.customerInsight as Record<string, unknown> | null;
  const campaigns = (data.campaigns || []) as Record<string, unknown>[];
  const summary = data.orchestrationSummary as Record<string, unknown> | undefined;

  let output = "";

  if (campaignTitle) {
    output += `🎯 "${campaignTitle}" Kampanyası\n\n`;
  }

  // Customer insight
  if (ci && typeof ci === "object" && Object.keys(ci).length > 0) {
    output += `👤 Müşteri Profili\n`;
    output += `  Segment: ${ci.ageSegment || "?"} | Değer: ${ci.valueSegment || "?"}\n`;
    output += `  Churn: ${ci.churnSegment || "?"} | Sadakat: ${ci.loyaltyTier || "?"}\n`;
    output += `  İlgi Alanı: ${ci.affinityCategory || "?"} (${ci.affinityType || "?"})\n\n`;
  }

  // Campaigns
  if (campaigns.length > 0) {
    output += `📋 Kampanya Önerileri (${campaigns.length} adet)\n\n`;
    campaigns.forEach((c, i) => {
      output += `${i + 1}. ${c.campaignName || c.name || "Kampanya"}\n`;
      if (c.targetCustomerSegment) output += `   🎯 Hedef: ${c.targetCustomerSegment}\n`;
      if (c.targetProductSegment) output += `   📦 Ürünler: ${String(c.targetProductSegment).slice(0, 80)}\n`;
      const timing = c.timing as Record<string, string> | undefined;
      if (timing) {
        output += `   📅 ${timing.startDate || "?"} → ${timing.endDate || "?"}`;
        if (timing.specialEvent) output += ` (${timing.specialEvent})`;
        output += "\n";
      }
      const ds = c.discountSuggestion as Record<string, string> | undefined;
      if (ds?.description) output += `   💰 ${ds.description}\n`;
      output += "\n";
    });
  } else {
    output += "⚠️ Kampanya üretilemedi.\n";
  }

  // Warnings
  const warnings = (summary?.warnings || []) as string[];
  if (warnings.length > 0) {
    output += `\n⚠️ Uyarılar:\n`;
    warnings.forEach((w) => (output += `  • ${w}\n`));
  }

  return output;
}

function formatError(err: Record<string, unknown>): string {
  return `❌ Hata: ${err.detail || err.message || JSON.stringify(err)}`;
}
