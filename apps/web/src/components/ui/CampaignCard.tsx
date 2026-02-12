"use client";

import { motion } from "framer-motion";
import {
  EnvelopeClosedIcon,
  MobileIcon,
  MagnifyingGlassIcon,
  ChatBubbleIcon,
  BellIcon,
  StarFilledIcon,
  SpeakerLoudIcon,
} from "@radix-ui/react-icons";
import type { IconProps } from "@radix-ui/react-icons/dist/types";
import type { ForwardRefExoticComponent, RefAttributes } from "react";

export interface Campaign {
  id: string;
  title: string;
  description: string;
  type: string;
  channel: string;
  estimatedReach: string;
  difficulty: "Kolay" | "Orta" | "Zor" | "N/A" | "Hata";
  products?: string[];
  discountRate?: number;
  targetSegment?: string;
  validUntil?: string;
}

const difficultyColors = {
  Kolay: "bg-green-500/20 text-green-400",
  Orta: "bg-yellow-500/20 text-yellow-400",
  Zor: "bg-red-500/20 text-red-400",
  "N/A": "bg-gray-500/20 text-gray-400",
  Hata: "bg-red-500/20 text-red-400",
};

type RadixIcon = ForwardRefExoticComponent<IconProps & RefAttributes<SVGSVGElement>>;

const channelIcons: Record<string, RadixIcon> = {
  "E-posta": EnvelopeClosedIcon,
  "Sosyal Medya": MobileIcon,
  "Google Ads": MagnifyingGlassIcon,
  "SMS": ChatBubbleIcon,
  "Push Bildirim": BellIcon,
  "Influencer": StarFilledIcon,
};

export default function CampaignCard({ campaign, index }: { campaign: Campaign; index: number }) {
  const ChannelIcon = channelIcons[campaign.channel] || SpeakerLoudIcon;

  const handleClick = () => {
    sessionStorage.setItem("selectedCampaign", JSON.stringify(campaign));
    window.location.href = "/campaign-studio";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      onClick={handleClick}
      className="bg-surface rounded-xl p-6 border border-gray-800 hover:border-primary/50 transition-all group cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <ChannelIcon className="w-5 h-5 text-primary-light" />
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${difficultyColors[campaign.difficulty]}`}>
          {campaign.difficulty}
        </span>
      </div>
      <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary-light transition-colors">
        {campaign.title}
      </h3>
      <p className="text-sm text-gray-400 mb-4 line-clamp-3">{campaign.description}</p>
      
      {/* Campaign Details */}
      {campaign.discountRate && (
        <div className="mb-3 flex items-center gap-2">
          <span className="text-xs bg-primary/20 text-primary-light px-2 py-1 rounded">
            %{campaign.discountRate} İndirim
          </span>
          {campaign.targetSegment && (
            <span className="text-xs bg-surface-light text-gray-400 px-2 py-1 rounded">
              {campaign.targetSegment}
            </span>
          )}
        </div>
      )}
      
      {/* Products */}
      {campaign.products && campaign.products.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-2">Kampanya Ürünleri ({campaign.products.length}):</p>
          <div className="space-y-1">
            {campaign.products.slice(0, 3).map((product, idx) => (
              <p key={idx} className="text-xs text-gray-400 truncate">• {product}</p>
            ))}
            {campaign.products.length > 3 && (
              <p className="text-xs text-gray-500">+{campaign.products.length - 3} ürün daha...</p>
            )}
          </div>
        </div>
      )}
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span className="bg-surface-light px-2 py-1 rounded">{campaign.channel}</span>
        <span>Erişim: {campaign.estimatedReach}</span>
      </div>
      
      {campaign.validUntil && (
        <div className="mt-2 text-xs text-gray-500">
          Geçerlilik: {campaign.validUntil}
        </div>
      )}
    </motion.div>
  );
}
