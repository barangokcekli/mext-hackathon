"use client";

import { motion } from "framer-motion";
import { RocketIcon } from "@radix-ui/react-icons";

export default function HeroSection() {
  return (
    <section className="text-center py-20 px-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center">
            <RocketIcon className="w-8 h-8 text-primary-light" />
          </div>
        </div>
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary-light to-accent bg-clip-text text-transparent">
          CampaignAI
        </h1>
        <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto mb-4">
          Ürün sayfanızın URL&apos;sini girin, yapay zeka sizin için
          en etkili kampanya önerilerini oluştursun.
        </p>
        <p className="text-sm text-gray-500">
          Saniyeler içinde akıllı kampanya fikirleri. Kurulum yok, kayıt yok.
        </p>
      </motion.div>
    </section>
  );
}
