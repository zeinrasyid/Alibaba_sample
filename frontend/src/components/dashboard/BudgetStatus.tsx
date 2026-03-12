"use client";

import { useEffect, useState } from "react";
import { PiggyBank, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { formatRupiah, calculateBudgetPercentage, calculateCategoryTotals } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Budget, Transaction, Category } from "@/types";

interface BudgetStatusProps {
  budgets: Budget[];
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

function AnimatedProgress({ value, className }: { value: number; className?: string }) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    // Delay to trigger the CSS transition after mount
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  return <Progress value={animatedValue} className={className} />;
}

export default function BudgetStatus({ budgets, transactions }: BudgetStatusProps) {
  const categoryTotals = calculateCategoryTotals(transactions);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.25 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <PiggyBank className="h-5 w-5 text-emerald-500" />
            Status Budget
          </CardTitle>
        </CardHeader>
        <CardContent>
          {budgets.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Belum ada budget yang diatur
            </p>
          ) : (
            <div className="space-y-5">
              {budgets.map((budget) => {
                const spent = categoryTotals[budget.category] || 0;
                const percentage = calculateBudgetPercentage(spent, budget.amount);
                const isWarning = percentage >= 80;
                const cappedPercentage = Math.min(percentage, 100);

                return (
                  <div key={budget.id} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">
                          {CATEGORY_LABELS[budget.category]}
                        </span>
                        {isWarning && (
                          <Badge
                            variant="destructive"
                            className="flex items-center gap-1 text-xs"
                          >
                            <AlertTriangle className="h-3 w-3" />
                            {percentage >= 100 ? "Melebihi" : "Hampir habis"}
                          </Badge>
                        )}
                      </div>
                      <span className="text-muted-foreground">
                        {formatRupiah(spent)} / {formatRupiah(budget.amount)}
                      </span>
                    </div>
                    <AnimatedProgress
                      value={cappedPercentage}
                      className={
                        isWarning
                          ? "[&>div]:bg-red-500"
                          : "[&>div]:bg-emerald-500"
                      }
                    />
                    <p className="text-xs text-muted-foreground text-right">
                      {percentage.toFixed(0)}%
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
