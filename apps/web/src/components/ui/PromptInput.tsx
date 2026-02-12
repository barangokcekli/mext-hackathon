"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PaperPlaneIcon,
  FileTextIcon,
  Cross2Icon,
  TargetIcon,
  RocketIcon,
  HeartIcon,
} from "@radix-ui/react-icons";

interface AttachedFile {
  name: string;
  content: string;
}

const quickPrompts = [
  {
    icon: TargetIcon,
    label: "Stok Eritme",
    text: "Elimdeki fazla stokları hızlıca eritmek için agresif bir kampanya oluştur. ",
    color: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  },
  {
    icon: RocketIcon,
    label: "Gelir Artırımı",
    text: "Satışları ve ortalama sepet tutarını artırmaya yönelik bir kampanya stratejisi oluştur. ",
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  },
  {
    icon: HeartIcon,
    label: "Müşteri Sadakati",
    text: "Mevcut müşterilerimin tekrar alışveriş yapmasını sağlayacak bir sadakat kampanyası oluştur. ",
    color: "text-pink-400 bg-pink-500/10 border-pink-500/20",
  },
];

const ACCEPTED_EXTENSIONS = ".json,.md,.txt,.csv,.xml,.yaml,.yml";

interface PromptInputProps {
  onSubmit: (prompt: string, files: AttachedFile[]) => void;
  isLoading: boolean;
}

export default function PromptInput({ onSubmit, isLoading }: PromptInputProps) {
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState<AttachedFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) onSubmit(prompt.trim(), files);
  };

  const handleQuickPrompt = (text: string) => {
    setPrompt((prev) => prev + text);
    textareaRef.current?.focus();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles) return;

    const newFiles: AttachedFile[] = [];
    for (const file of Array.from(selectedFiles)) {
      const content = await file.text();
      newFiles.push({ name: file.name, content });
    }
    setFiles((prev) => [...prev, ...newFiles]);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-3xl mx-auto w-full px-4"
    >
      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2 mb-4">
        {quickPrompts.map((qp) => {
          const Icon = qp.icon;
          return (
            <button
              key={qp.label}
              type="button"
              onClick={() => handleQuickPrompt(qp.text)}
              disabled={isLoading}
              className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer disabled:opacity-50 ${qp.color}`}
            >
              <Icon className="w-3.5 h-3.5" />
              {qp.label}
            </button>
          );
        })}
      </div>

      {/* Main input */}
      <form onSubmit={handleSubmit}>
        <div className="bg-surface rounded-2xl border border-gray-800 focus-within:border-primary/50 transition-all">
          {/* Attached files */}
          <AnimatePresence>
            {files.length > 0 && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="px-4 pt-3 flex flex-wrap gap-2 overflow-hidden"
              >
                {files.map((file, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-light text-xs text-gray-300 border border-gray-700"
                  >
                    <FileTextIcon className="w-3 h-3 text-primary-light" />
                    {file.name}
                    <button
                      type="button"
                      onClick={() => removeFile(i)}
                      className="ml-0.5 text-gray-500 hover:text-red-400 transition-colors cursor-pointer"
                      aria-label={`${file.name} dosyasını kaldır`}
                    >
                      <Cross2Icon className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Textarea + actions */}
          <div className="flex items-end gap-2 p-3">
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (prompt.trim()) onSubmit(prompt.trim(), files);
                }
              }}
              placeholder="Kampanyanız için yapay zekaya talimat verin..."
              disabled={isLoading}
              rows={3}
              className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none text-sm leading-relaxed disabled:opacity-50"
              aria-label="Kampanya prompt alanı"
            />
            <div className="flex items-center gap-1.5 shrink-0 pb-0.5">
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_EXTENSIONS}
                multiple
                onChange={handleFileChange}
                className="hidden"
                aria-label="Dosya ekle"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                className="p-2 rounded-lg text-gray-500 hover:text-primary-light hover:bg-surface-light transition-all cursor-pointer disabled:opacity-50"
                title="Dosya ekle (.json, .md, .txt, .csv, .xml, .yaml)"
                aria-label="Dosya ekle"
              >
                <FileTextIcon className="w-4 h-4" />
              </button>
              <button
                type="submit"
                disabled={isLoading || !prompt.trim()}
                className="p-2 rounded-lg bg-primary hover:bg-primary-dark text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                aria-label="Gönder"
              >
                <PaperPlaneIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </form>

      <p className="text-xs text-gray-600 mt-2 text-center">
        Shift+Enter ile yeni satır, Enter ile gönder. Dosya ekleyerek AI&apos;a ek bağlam sağlayabilirsiniz.
      </p>
    </motion.div>
  );
}
