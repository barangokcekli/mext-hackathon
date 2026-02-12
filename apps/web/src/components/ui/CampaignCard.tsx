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
  difficulty: "Kolay" | "Orta" | "Zor";
}

const difficultyColors = {
  Kolay: "bg-green-500/20 text-green-400",
  Orta: "bg-yellow-500/20 text-yellow-400",
  Zor: "bg-red-500/20 text-red-400",
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
      <p className="text-sm text-gray-400 mb-4 line-clamp-2">{campaign.description}</p>
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span className="bg-surface-light px-2 py-1 rounded">{campaign.channel}</span>
        <span>Tahmini Erişim: {campaign.estimatedReach}</span>
      </div>
    </motion.div>
  );
}
