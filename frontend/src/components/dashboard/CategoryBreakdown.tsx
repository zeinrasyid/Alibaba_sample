"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { calculateCategoryTotals, formatRupiah } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Transaction, Category } from "@/types";

interface CategoryBreakdownProps {
  transactions: Transaction[];
}

const CATEGORY_COLORS: Record<Category, string> = {
  food: "#10b981",
  transport: "#3b82f6",
  shopping: "#f59e0b",
  entertainment: "#8b5cf6",
  health: "#ef4444",
  bills: "#6366f1",
  education: "#14b8a6",
  other: "#6b7280",
};

const CATEGORY_LABELS: Record<Category, string> = {
  food: "Makanan",
  transport: "Transport",
  shopping: "Belanja",
  entertainment: "Hiburan",
  health: "Kesehatan",
  bills: "Tagihan",
  education: "Pendidikan",
  other: "Lainnya",
};

export default function CategoryBreakdown({ transactions }: CategoryBreakdownProps) {
  const totals = calculateCategoryTotals(transactions);

  const data = Object.entries(totals)
    .filter(([, value]) => value > 0)
    .map(([category, value]) => ({
      category: CATEGORY_LABELS[category as Category],
      amount: value,
      color: CATEGORY_COLORS[category as Category],
    }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.15 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="text-lg">Pengeluaran per Kategori</CardTitle>
        </CardHeader>
        <CardContent>
          {data.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Belum ada data pengeluaran
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                <XAxis
                  dataKey="category"
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => formatRupiah(v).replace("Rp ", "")}
                />
                <Tooltip
                  formatter={(value) => [formatRupiah(Number(value)), "Jumlah"]}
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid #e5e7eb",
                    fontSize: "13px",
                  }}
                />
                <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
                  {data.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
