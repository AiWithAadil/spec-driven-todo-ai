/**
 * API client service with Bearer token handling
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private getAuthToken(): string | null {
    if (typeof window === "undefined") return null;
    const token = localStorage.getItem("auth_token");
    console.log(`[API] Auth token found: ${!!token}, length: ${token?.length || 0}`);
    return token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    const token = this.getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
      console.log(`[API] Added Authorization header with token: ${token.substring(0, 30)}...`);
    } else {
      console.log("[API] No auth token found - request will be unauthenticated");
    }

    return headers;
  }

  async request<T>(
    method: string,
    path: string,
    body?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers = this.getHeaders();

    const options: RequestInit = {
      method,
      headers,
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    console.log(`[API] ${method} ${url}`, { headers, hasBody: !!body });
    const response = await fetch(url, options);

    if (!response.ok) {
      console.error(`[API] Error ${response.status}: ${response.statusText}`);
      try {
        const error = await response.json();
        throw new Error(error.detail || `API error: ${response.statusText}`);
      } catch (e) {
        if (e instanceof Error && e.message.includes("detail")) {
          throw e;
        }
        throw new Error(`API error: ${response.statusText}`);
      }
    }

    if (response.status === 204) {
      return null as unknown as T;
    }

    return await response.json();
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>("GET", path);
  }

  post<T>(path: string, body: any): Promise<T> {
    return this.request<T>("POST", path, body);
  }

  put<T>(path: string, body: any): Promise<T> {
    return this.request<T>("PUT", path, body);
  }

  patch<T>(path: string, body: any): Promise<T> {
    return this.request<T>("PATCH", path, body);
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
}

export const apiClient = new ApiClient();
