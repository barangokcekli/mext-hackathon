"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import {
  MagnifyingGlassIcon,
  LightningBoltIcon,
  BarChartIcon,
  StarIcon,
  RocketIcon,
  CheckIcon,
} from "@radix-ui/react-icons";

const steps = [
  { icon: MagnifyingGlassIcon, text: "Ürün sayfası taranıyor..." },
  { icon: LightningBoltIcon, text: "Yapay zeka ürünü analiz ediyor..." },
  { icon: BarChartIcon, text: "Hedef kitle belirleniyor..." },
  { icon: StarIcon, text: "Kampanya önerileri oluşturuluyor..." },
  { icon: RocketIcon, text: "Son rötuşlar yapılıyor..." },
];

export default function LoadingAnimation() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  const CurrentMainIcon = steps[currentStep].icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-lg mx-auto mt-12 px-4"
    >
      <div className="bg-surface rounded-2xl p-8 border border-gray-800">
        {/* Pulse ring */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <motion.div
              className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <motion.div
                className="w-12 h-12 rounded-full bg-primary/40 flex items-center justify-center"
                animate={{ scale: [1, 1.15, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <CurrentMainIcon className="w-6 h-6 text-primary-light" />
              </motion.div>
            </motion.div>
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-primary/30"
              animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {steps.map((step, i) => {
            const StepIcon = step.icon;
            return (
              <AnimatePresence key={i}>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{
                    opacity: i <= currentStep ? 1 : 0.3,
                    x: 0,
                  }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      i < currentStep
                        ? "bg-green-500/20 text-green-400"
                        : i === currentStep
                        ? "bg-primary/20 text-primary-light"
                        : "bg-gray-800 text-gray-600"
                    }`}
                  >
                    {i < currentStep ? (
                      <CheckIcon className="w-4 h-4" />
                    ) : (
                      <StepIcon className="w-4 h-4" />
                    )}
                  </div>
                  <span
                    className={`text-sm ${
                      i <= currentStep ? "text-gray-300" : "text-gray-600"
                    }`}
                  >
                    {step.text}
                  </span>
                  {i === currentStep && (
                    <motion.div
                      className="ml-auto flex gap-1"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      {[0, 1, 2].map((dot) => (
                        <motion.div
                          key={dot}
                          className="w-1.5 h-1.5 rounded-full bg-primary-light"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            delay: dot * 0.2,
                          }}
                        />
                      ))}
                    </motion.div>
                  )}
                </motion.div>
              </AnimatePresence>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
