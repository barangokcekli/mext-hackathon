"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface UrlInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

export default function UrlInput({ onSubmit, isLoading }: UrlInputProps) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) onSubmit(url.trim());
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="max-w-2xl mx-auto px-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/urun-sayfasi"
          required
          disabled={isLoading}
          className="flex-1 px-5 py-4 rounded-xl bg-surface-light border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg disabled:opacity-50"
          aria-label="Ürün URL adresi"
        />
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="px-8 py-4 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer whitespace-nowrap"
        >
          {isLoading ? "Analiz ediliyor..." : "Kampanya Oluştur"}
        </button>
      </div>
    </motion.form>
  );
}
