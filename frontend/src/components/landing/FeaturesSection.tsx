"use client";

import { motion } from "framer-motion";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const features = [
  {
    emoji: "📝",
    title: "Pencatatan Transaksi",
    description: "Catat pemasukan dan pengeluaran dengan mudah lewat chat Telegram.",
  },
  {
    emoji: "💰",
    title: "Manajemen Budget",
    description: "Atur budget per kategori dan pantau penggunaannya secara real-time.",
  },
  {
    emoji: "📊",
    title: "Insight Pengeluaran",
    description: "Dapatkan analisis dan insight tentang pola pengeluaranmu.",
  },
  {
    emoji: "📈",
    title: "Chart Keuangan",
    description: "Visualisasi data keuangan dengan chart yang mudah dipahami.",
  },
  {
    emoji: "⚠️",
    title: "Peringatan Budget",
    description: "Terima peringatan otomatis saat pengeluaran mendekati batas budget.",
  },
  {
    emoji: "🤖",
    title: "Integrasi Telegram",
    description: "Kelola keuangan langsung dari Telegram tanpa perlu buka aplikasi lain.",
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function FeaturesSection() {
  return (
    <section id="features" className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Fitur Utama
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Semua yang kamu butuhkan untuk mengelola keuangan pribadi
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature) => (
            <motion.div key={feature.title} variants={cardVariants}>
              <Card className="h-full hover:shadow-lg transition-shadow duration-300 border-border/50">
                <CardHeader>
                  <div className="text-4xl mb-3">{feature.emoji}</div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription className="text-sm leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
