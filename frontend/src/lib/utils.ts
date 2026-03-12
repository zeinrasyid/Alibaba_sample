import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Category, Transaction } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validateUsername(username: string): boolean {
  return username.trim().length > 0;
}

export function formatRupiah(amount: number): string {
  const formatted = new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);

  // Intl returns "Rp\u00a0..." — normalize to "Rp " with a regular space
  return formatted.replace(/\u00a0/, " ");
}

const ALL_CATEGORIES: Category[] = [
  "food",
  "transport",
  "shopping",
  "entertainment",
  "health",
  "bills",
  "education",
  "other",
];

export function calculateCategoryTotals(
  transactions: Transaction[]
): Record<Category, number> {
  const totals = {} as Record<Category, number>;
  for (const cat of ALL_CATEGORIES) {
    totals[cat] = 0;
  }

  for (const tx of transactions) {
    if (tx.type === "expense") {
      totals[tx.category] += tx.amount;
    }
  }

  return totals;
}

export function calculateBudgetPercentage(
  spent: number,
  budget: number
): number {
  if (budget === 0) return 0;
  return (spent / budget) * 100;
}
