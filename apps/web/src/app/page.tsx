"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import HeroSection from "@/components/ui/HeroSection";
import UrlInput from "@/components/ui/UrlInput";
import LoadingAnimation from "@/components/ui/LoadingAnimation";
import Link from "next/link";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      // Store in sessionStorage for the campaigns page
      sessionStorage.setItem("campaignData", JSON.stringify(data));
      router.push("/campaigns");
    } catch {
      setIsLoading(false);
      alert("Bir hata oluştu. Lütfen tekrar deneyin.");
    }
  };

  return (
    <main className="min-h-screen flex flex-col justify-center">
      {!isLoading && (
        <>
          <HeroSection />
          <UrlInput onSubmit={handleSubmit} isLoading={isLoading} />
          <div className="text-center mt-6">
            <Link
              href="/campaign-studio"
              className="text-sm text-gray-500 hover:text-primary-light transition-colors"
            >
              veya URL olmadan direkt kampanya stüdyosuna git →
            </Link>
          </div>
        </>
      )}
      {isLoading && <LoadingAnimation />}
    </main>
  );
}
