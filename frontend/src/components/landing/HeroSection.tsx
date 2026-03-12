"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import GraceImage from "../../../images/Grace.png";

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 via-white to-teal-50" />
      <div className="absolute top-20 right-10 w-72 h-72 bg-emerald-200/30 rounded-full blur-3xl" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-teal-200/20 rounded-full blur-3xl" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Text Content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center md:text-left"
          >
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-foreground">
              <span className="text-emerald-600">Grace</span> - Your Financial
              Assistant
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-lg">
              Kelola keuanganmu dengan mudah melalui Telegram. Catat transaksi,
              atur budget, dan dapatkan insight keuangan — semua lewat chat.
            </p>
            <div className="mt-8">
              <Button size="lg" asChild className="text-base px-8 py-6">
                <Link href="/register">Mulai Sekarang</Link>
              </Button>
            </div>
          </motion.div>

          {/* Grace Image */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex justify-center"
          >
            <Image
              src={GraceImage}
              alt="Grace - Financial Assistant"
              width={400}
              height={400}
              priority
              className="drop-shadow-2xl"
            />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
