"use client";

import { useEffect, useState } from "react";
import { LogOut } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { getTransactions, getBudgets } from "@/lib/api";
import { Button } from "@/components/ui/button";
import AuthGuard from "@/components/shared/AuthGuard";
import DashboardSkeleton from "@/components/dashboard/DashboardSkeleton";
import ApiKeyManager from "@/components/dashboard/ApiKeyManager";
import ExpenseSummary from "@/components/dashboard/ExpenseSummary";
import CategoryBreakdown from "@/components/dashboard/CategoryBreakdown";
import RecentTransactions from "@/components/dashboard/RecentTransactions";
import BudgetStatus from "@/components/dashboard/BudgetStatus";
import type { Transaction, Budget } from "@/types";

function DashboardContent() {
  const { user, logout } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      if (!user) return;
      try {
        const [txData, budgetData] = await Promise.all([
          getTransactions(user.email),
          getBudgets(user.email),
        ]);
        setTransactions(txData);
        setBudgets(budgetData);
      } catch {
        // Data fetch failed — show empty state
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, [user]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50/50 to-white">
        <div className="mx-auto max-w-6xl px-4 py-8">
          <DashboardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50/50 to-white">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="space-y-6">
        {/* Header */}
        <motion.div
          className="flex items-center justify-between"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div>
            <h1 className="text-2xl font-bold">
              Halo, {user?.username ?? "User"} 👋
            </h1>
            <p className="text-sm text-muted-foreground">
              Selamat datang di dashboard Grace
            </p>
          </div>
          <Button variant="outline" onClick={logout} className="hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors">
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </motion.div>

        {/* API Key Manager — full width */}
        <ApiKeyManager />

        {/* Summary + Chart — 2 columns on desktop */}
        <div className="grid gap-6 md:grid-cols-2">
          <ExpenseSummary transactions={transactions} />
          <CategoryBreakdown transactions={transactions} />
        </div>

        {/* Transactions + Budget — 2 columns on desktop */}
        <div className="grid gap-6 md:grid-cols-2">
          <RecentTransactions transactions={transactions} />
          <BudgetStatus budgets={budgets} transactions={transactions} />
        </div>
      </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  );
}
