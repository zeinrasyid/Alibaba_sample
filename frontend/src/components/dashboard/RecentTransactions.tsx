import { Receipt } from "lucide-react";
import { motion } from "framer-motion";
import { formatRupiah } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Transaction, Category } from "@/types";

interface RecentTransactionsProps {
  transactions: Transaction[];
}

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

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function RecentTransactions({ transactions }: RecentTransactionsProps) {
  const sorted = [...transactions].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Receipt className="h-5 w-5 text-emerald-500" />
            Transaksi Terbaru
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sorted.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Belum ada transaksi
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 font-medium">Tanggal</th>
                    <th className="pb-2 font-medium">Deskripsi</th>
                    <th className="pb-2 font-medium">Kategori</th>
                    <th className="pb-2 text-right font-medium">Jumlah</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((tx) => (
                    <tr key={tx.id} className="border-b last:border-0">
                      <td className="py-3 whitespace-nowrap">
                        {formatDate(tx.date)}
                      </td>
                      <td className="py-3">{tx.description}</td>
                      <td className="py-3">
                        <Badge variant="secondary" className="text-xs">
                          {CATEGORY_LABELS[tx.category]}
                        </Badge>
                      </td>
                      <td className="py-3 text-right whitespace-nowrap font-medium">
                        {tx.type === "expense" ? "-" : "+"}
                        {formatRupiah(tx.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
