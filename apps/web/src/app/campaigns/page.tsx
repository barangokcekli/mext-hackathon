"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeftIcon, PlusCircledIcon } from "@radix-ui/react-icons";
import CampaignCard from "@/components/ui/CampaignCard";
import type { Campaign } from "@/components/ui/CampaignCard";

interface CampaignData {
  campaigns: Campaign[];
  analyzedUrl: string;
  orchestrationSummary?: {
    customerAnalyzed: boolean;
    productAnalyzed: boolean;
    campaignCount: number;
    warnings?: string[];
  };
  customerInsight?: any;
  productInsight?: any;
}

export default function CampaignsPage() {
  const [data, setData] = useState<CampaignData | null>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = sessionStorage.getItem("campaignData");
    if (!stored) {
      router.push("/");
      return;
    }
    setData(JSON.parse(stored));
  }, [router]);

  if (!data) return null;

  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <button
            onClick={() => router.push("/")}
            className="text-sm text-gray-500 hover:text-primary-light transition-colors mb-6 inline-flex items-center gap-2 cursor-pointer"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Yeni Analiz
          </button>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
            📋 Kampanya Önerileri ({data.campaigns.length} adet)
          </h1>
          <p className="text-gray-400">
            <span className="text-primary-light">{data.analyzedUrl}</span> için{" "}
            {data.campaigns.length} kampanya önerisi oluşturuldu.
          </p>
          
          {/* Orchestration Summary */}
          {data.orchestrationSummary && (
            <div className="mt-4 p-4 bg-surface rounded-lg border border-gray-800">
              <div className="flex items-center gap-4 text-sm">
                <span className={data.orchestrationSummary.customerAnalyzed ? "text-green-400" : "text-gray-500"}>
                  {data.orchestrationSummary.customerAnalyzed ? "✓" : "✗"} Müşteri Analizi
                </span>
                <span className={data.orchestrationSummary.productAnalyzed ? "text-green-400" : "text-gray-500"}>
                  {data.orchestrationSummary.productAnalyzed ? "✓" : "✗"} Ürün Analizi
                </span>
              </div>
              {data.orchestrationSummary.warnings && data.orchestrationSummary.warnings.length > 0 && (
                <div className="mt-2 text-xs text-yellow-400">
                  ⚠️ Uyarılar:
                  {data.orchestrationSummary.warnings.map((warning, idx) => (
                    <div key={idx} className="ml-4">• {warning}</div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          <button
            onClick={() => {
              sessionStorage.removeItem("selectedCampaign");
              router.push("/campaign-studio");
            }}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 border border-primary/20 text-primary-light text-sm hover:bg-primary/20 transition-all cursor-pointer"
          >
            <PlusCircledIcon className="w-4 h-4" />
            Sıfırdan Kampanya Oluştur
          </button>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {data.campaigns.map((campaign, i) => (
            <CampaignCard key={campaign.id} campaign={campaign} index={i} />
          ))}
        </div>
      </div>
    </main>
  );
}
