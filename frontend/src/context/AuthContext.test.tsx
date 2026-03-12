import { render, screen, act, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AuthProvider, useAuth } from "./AuthContext";

// Mock the api module
vi.mock("@/lib/api", () => ({
  getUser: vi.fn(),
  ApiRequestError: class ApiRequestError extends Error {
    status: number;
    constructor(status: number, message: string) {
      super(message);
      this.name = "ApiRequestError";
      this.status = status;
    }
  },
}));

import { getUser, ApiRequestError } from "@/lib/api";

const STORAGE_KEY = "grace_session";

// Helper component to access auth context
function TestConsumer() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(isLoading)}</span>
      <span data-testid="authenticated">{String(isAuthenticated)}</span>
      <span data-testid="user">{user ? JSON.stringify(user) : "null"}</span>
      <button data-testid="login" onClick={() => login("test@example.com")} />
      <button data-testid="logout" onClick={() => logout()} />
    </div>
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("starts with isLoading true then resolves to false", async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(screen.getByTestId("user").textContent).toBe("null");
  });

  it("restores session from localStorage on mount", async () => {
    const session = { email: "user@test.com", username: "user@test.com" };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("true");
    expect(screen.getByTestId("user").textContent).toBe(JSON.stringify(session));
  });

  it("handles invalid localStorage data gracefully", async () => {
    localStorage.setItem(STORAGE_KEY, "not-valid-json");

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it("login saves session when getUser returns 404 (email not found)", async () => {
    const mockGetUser = getUser as ReturnType<typeof vi.fn>;
    mockGetUser.mockRejectedValue(
      new ApiRequestError(404, "User not found")
    );

    let loginError: Error | null = null;

    function TestLoginNotFound() {
      const { login, isLoading } = useAuth();
      return (
        <div>
          <span data-testid="loading">{String(isLoading)}</span>
          <button
            data-testid="login-notfound"
            onClick={async () => {
              try {
                await login("test@example.com");
              } catch (e) {
                loginError = e as Error;
              }
            }}
          />
        </div>
      );
    }

    render(
      <AuthProvider>
        <TestLoginNotFound />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    await act(async () => {
      screen.getByTestId("login-notfound").click();
    });

    expect(loginError).not.toBeNull();
    expect(loginError!.message).toContain("tidak ditemukan");
  });

  it("login saves session when getUser succeeds (user exists)", async () => {
    const mockGetUser = getUser as ReturnType<typeof vi.fn>;
    mockGetUser.mockResolvedValue({
      id: 0,
      username: "existinguser",
      email: "test@example.com",
      created_at: new Date().toISOString(),
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    await act(async () => {
      screen.getByTestId("login").click();
    });

    expect(screen.getByTestId("authenticated").textContent).toBe("true");
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
    expect(stored.email).toBe("test@example.com");
  });

  it("login throws on non-404 errors", async () => {
    const mockGetUser = getUser as ReturnType<typeof vi.fn>;
    mockGetUser.mockRejectedValue(
      new ApiRequestError(500, "Server error")
    );

    let loginError: Error | null = null;

    function TestLoginError() {
      const { login, isLoading } = useAuth();
      return (
        <div>
          <span data-testid="loading">{String(isLoading)}</span>
          <button
            data-testid="login-err"
            onClick={async () => {
              try {
                await login("test@example.com");
              } catch (e) {
                loginError = e as Error;
              }
            }}
          />
        </div>
      );
    }

    render(
      <AuthProvider>
        <TestLoginError />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    await act(async () => {
      screen.getByTestId("login-err").click();
    });

    expect(loginError).not.toBeNull();
    expect(loginError!.message).toBe("Server error");
  });

  it("logout clears session from state and localStorage", async () => {
    const session = { email: "user@test.com", username: "user@test.com" };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("authenticated").textContent).toBe("true");
    });

    await act(async () => {
      screen.getByTestId("logout").click();
    });

    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(screen.getByTestId("user").textContent).toBe("null");
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });

  it("useAuth throws when used outside AuthProvider", () => {
    function Orphan() {
      useAuth();
      return null;
    }

    expect(() => render(<Orphan />)).toThrow(
      "useAuth must be used within an AuthProvider"
    );
  });
});
