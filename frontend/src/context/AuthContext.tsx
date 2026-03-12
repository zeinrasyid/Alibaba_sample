"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { UserSession } from "@/types";
import { getUser, ApiRequestError } from "@/lib/api";

const STORAGE_KEY = "grace_session";

interface AuthContextType {
  user: UserSession | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login(email: string): Promise<void>;
  logout(): void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore session from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const session: UserSession = JSON.parse(stored);
        if (session.email) {
          setUser(session);
        }
      }
    } catch {
      // Invalid JSON or missing data — ignore
      localStorage.removeItem(STORAGE_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string): Promise<void> => {
    try {
      // Use GET /users/{email} to verify the user exists
      const response = await getUser(email);
      const session: UserSession = {
        email: response.email,
        username: response.username,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
      setUser(session);
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 404) {
        // User not found
        throw new ApiRequestError(404, "Email tidak ditemukan, silakan daftar terlebih dahulu");
      }
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  }, []);

  const isAuthenticated = user !== null;

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, isLoading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export { AuthContext };
