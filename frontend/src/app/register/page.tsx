"use client";

import { useState, useEffect, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createUser, ApiRequestError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { validateEmail, validateUsername } from "@/lib/utils";

export default function RegisterPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [errors, setErrors] = useState<{ username?: string; email?: string; inviteCode?: string; form?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    // Client-side validation
    const newErrors: { username?: string; email?: string; inviteCode?: string } = {};

    if (!validateUsername(username)) {
      newErrors.username = "Username tidak boleh kosong";
    }
    if (!email.trim()) {
      newErrors.email = "Email tidak boleh kosong";
    } else if (!validateEmail(email)) {
      newErrors.email = "Format email tidak valid";
    }
    if (!inviteCode.trim()) {
      newErrors.inviteCode = "Invite code tidak boleh kosong";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setIsSubmitting(true);

    try {
      await createUser(username.trim(), email.trim(), inviteCode.trim());
      toast.success("Pendaftaran berhasil! Silakan login");
      router.push("/login?registered=true");
    } catch (error) {
      if (error instanceof ApiRequestError) {
        if (error.status === 403) {
          setErrors({ inviteCode: "Invite code tidak valid" });
        } else if (error.status === 400) {
          setErrors({ form: "Email sudah terdaftar" });
        } else {
          setErrors({ form: "Terjadi kesalahan, silakan coba lagi" });
        }
      } else {
        setErrors({ form: "Terjadi kesalahan, silakan coba lagi" });
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return null;
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 via-white to-teal-50" />
      <div className="absolute top-20 right-10 w-72 h-72 bg-emerald-200/30 rounded-full blur-3xl" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-teal-200/20 rounded-full blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md mx-auto px-4"
      >
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold">
              <span className="text-emerald-600">Grace</span> — Daftar
            </CardTitle>
            <CardDescription>
              Buat akun untuk mulai mengelola keuanganmu
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {errors.form && (
                <p className="text-sm text-destructive text-center" role="alert">
                  {errors.form}
                </p>
              )}

              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Masukkan username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  aria-invalid={!!errors.username}
                />
                {errors.username && (
                  <p className="text-sm text-destructive">{errors.username}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Masukkan email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  aria-invalid={!!errors.email}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="inviteCode">Invite Code</Label>
                <Input
                  id="inviteCode"
                  type="text"
                  placeholder="Masukkan invite code"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value)}
                  aria-invalid={!!errors.inviteCode}
                />
                {errors.inviteCode && (
                  <p className="text-sm text-destructive">{errors.inviteCode}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Mendaftar..." : "Daftar"}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-muted-foreground">
              Sudah punya akun?{" "}
              <Link href="/login" className="text-emerald-600 hover:underline font-medium">
                Login
              </Link>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
