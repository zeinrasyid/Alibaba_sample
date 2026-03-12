"use client";

import { motion } from "framer-motion";

const steps = [
  {
    number: 1,
    emoji: "📋",
    title: "Daftar",
    description: "Buat akun gratis di website Grace dengan username dan email.",
  },
  {
    number: 2,
    emoji: "🔑",
    title: "Generate API Key",
    description: "Generate API key unik dari dashboard untuk autentikasi.",
  },
  {
    number: 3,
    emoji: "💬",
    title: "Login di Telegram",
    description: "Buka bot Grace di Telegram dan kirim /login dengan API key.",
  },
  {
    number: 4,
    emoji: "🚀",
    title: "Mulai Chat",
    description: "Mulai catat transaksi dan kelola keuangan lewat chat.",
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const stepVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Cara Kerja
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Mulai kelola keuanganmu dalam 4 langkah mudah
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8"
        >
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              variants={stepVariants}
              className="relative flex flex-col items-center text-center"
            >
              {/* Connector line (hidden on first item and mobile) */}
              {index > 0 && (
                <div className="hidden lg:block absolute top-8 -left-4 w-8 h-0.5 bg-emerald-300" />
              )}

              {/* Step circle */}
              <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center text-2xl mb-4">
                {step.emoji}
              </div>

              {/* Step number */}
              <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider mb-2">
                Langkah {step.number}
              </span>

              <h3 className="text-lg font-semibold text-foreground mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
