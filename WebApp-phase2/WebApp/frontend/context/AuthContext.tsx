"use client";

/**
 * Authentication context for managing user state
 */

import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { User, AuthContextType } from "../types/auth";
import { authService } from "../services/auth";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = authService.getToken();
    const storedUser = localStorage.getItem("user");
    console.log("[AUTH] Initializing - Token found:", !!token);
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("[AUTH] Failed to parse stored user:", e);
        authService.clearToken();
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.login(email, password);
      authService.storeToken(response.access_token);
      localStorage.setItem("user", JSON.stringify(response.user));
      setUser(response.user);
      console.log("[AUTH] Login successful:", response.user);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Login failed";
      setError(errorMessage);
      console.error("[AUTH] Login error:", err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, password_confirm: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.register(email, password, password_confirm);
      authService.storeToken(response.access_token);
      localStorage.setItem("user", JSON.stringify(response.user));
      setUser(response.user);
      console.log("[AUTH] Registered and token stored:", response.access_token);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Registration failed";
      setError(errorMessage);
      console.error("[AUTH] Registration error:", err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.clearToken();
    localStorage.removeItem("user");
    setUser(null);
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
