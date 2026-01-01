/**
 * Authentication service
 */

import { apiClient } from "./api";
import { AuthResponse, RegisterRequest, LoginRequest } from "../types/auth";

export const authService = {
  register: async (email: string, password: string, password_confirm: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>("/api/v1/auth/register", {
      email,
      password,
      password_confirm,
    });
    return response;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>("/api/v1/auth/login", {
      email,
      password,
    });
    return response;
  },

  storeToken: (token: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  },

  getToken: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("auth_token");
  },

  clearToken: (): void => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  },

  isAuthenticated: (): boolean => {
    return !!authService.getToken();
  },
};
