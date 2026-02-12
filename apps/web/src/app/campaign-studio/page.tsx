"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeftIcon, LightningBoltIcon } from "@radix-ui/react-icons";
import PromptInput from "@/components/ui/PromptInput";

interface AttachedFile {
  name: string;
  content: string;
}

export default function CampaignStudioPage() {
  const [campaignTitle, setCampaignTitle] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = sessionStorage.getItem("selectedCampaign");
    if (stored) {
      const campaign = JSON.parse(stored);
      setCampaignTitle(campaign.title);
    }
  }, []);

  const handleSubmit = async (prompt: string, files: AttachedFile[]) => {
    setIsLoading(true);
    setResult(null);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          prompt, 
          files, 
          campaignTitle,
          customerId: "C-2001" // Default customer
        }),
      });
      const data = await res.json();
      setResult(data.result);
    } catch {
      setResult("Bir hata oluştu. Lütfen tekrar deneyin.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <button
            onClick={() => router.back()}
            className="text-sm text-gray-500 hover:text-primary-light transition-colors mb-6 inline-flex items-center gap-2 cursor-pointer"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Geri
          </button>

          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
              <LightningBoltIcon className="w-5 h-5 text-primary-light" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              Kampanya Stüdyosu
            </h1>
          </div>
          {campaignTitle && (
            <p className="text-gray-400 ml-13">
              <span className="text-primary-light">{campaignTitle}</span> için içerik oluşturun
            </p>
          )}
          {!campaignTitle && (
            <p className="text-gray-400 ml-13">
              Yapay zekaya kampanya talimatlarınızı verin
            </p>
          )}
        </motion.div>

        <PromptInput onSubmit={handleSubmit} isLoading={isLoading} />

        {/* Loading state */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8 flex justify-center"
          >
            <div className="flex items-center gap-3 text-gray-400">
              <motion.div
                className="w-5 h-5 rounded-full border-2 border-primary border-t-transparent"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              AI kampanya içeriğinizi oluşturuyor...
            </div>
          </motion.div>
        )}

        {/* Result */}
        {result && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 bg-surface rounded-2xl border border-gray-800 p-6"
          >
            <h2 className="text-lg font-semibold text-white mb-4">AI Çıktısı</h2>
            <div className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
              {result}
            </div>
          </motion.div>
        )}
      </div>
    </main>
  );
}
