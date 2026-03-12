"use client";

import { useState } from "react";
import { Copy, Key, Plus } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { generateApiKey } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ApiKeyResponse } from "@/types";

export default function ApiKeyManager() {
  const { user } = useAuth();
  const [keys, setKeys] = useState<ApiKeyResponse[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  async function handleGenerate() {
    if (!user) return;
    setIsGenerating(true);
    try {
      const response = await generateApiKey(user.username, user.email);
      setKeys((prev) => [response, ...prev]);
      toast.success("API Key berhasil di-generate!");
    } catch {
      toast.error("Gagal generate API key, silakan coba lagi");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleCopy(apiKey: string) {
    try {
      await navigator.clipboard.writeText(apiKey);
      toast.success("API Key berhasil disalin");
    } catch {
      toast.error("Gagal menyalin API Key");
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Key className="h-5 w-5 text-emerald-500" />
            API Key Management
          </CardTitle>
          <CardDescription>
            Generate API key untuk login ke Grace di Telegram
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button onClick={handleGenerate} disabled={isGenerating}>
            <Plus className="h-4 w-4" />
            {isGenerating ? "Generating..." : "Generate API Key"}
          </Button>

          {keys.length > 0 && (
            <div className="space-y-3">
              {keys.map((k, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 rounded-lg border bg-muted/50 p-3"
                >
                  <code className="flex-1 truncate text-sm font-mono">
                    {k.api_key}
                  </code>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleCopy(k.api_key)}
                    title="Salin API Key"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-950/30">
            <p className="text-sm font-medium text-emerald-800 dark:text-emerald-300">
              Cara menggunakan API Key:
            </p>
            <p className="mt-1 text-sm text-emerald-700 dark:text-emerald-400">
              Buka bot Grace di Telegram → kirim{" "}
              <Badge variant="secondary" className="font-mono text-xs">
                /login {"<API_KEY>"}
              </Badge>
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
