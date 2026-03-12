import { Wallet } from "lucide-react";
import { motion } from "framer-motion";
import { formatRupiah } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Transaction } from "@/types";

interface ExpenseSummaryProps {
  transactions: Transaction[];
}

const MONTH_NAMES = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember",
];

export default function ExpenseSummary({ transactions }: ExpenseSummaryProps) {
  const now = new Date();
  const currentMonth = MONTH_NAMES[now.getMonth()];
  const currentYear = now.getFullYear();

  const total = transactions
    .filter((t) => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Wallet className="h-5 w-5 text-emerald-500" />
            Total Pengeluaran
          </CardTitle>
          <CardDescription>
            {currentMonth} {currentYear}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-emerald-600">
            {formatRupiah(total)}
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
}
