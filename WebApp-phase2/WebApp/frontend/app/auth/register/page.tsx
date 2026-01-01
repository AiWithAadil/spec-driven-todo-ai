"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../../../context/AuthContext";

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error: authError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password || !passwordConfirm) {
      setError("All fields are required");
      return;
    }

    if (password !== passwordConfirm) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    try {
      await register(email, password, passwordConfirm);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.formContainer}>
        <h1>Create Account</h1>

        <form onSubmit={handleSubmit}>
          <div style={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              disabled={isLoading}
              required
            />
          </div>

          <div style={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              disabled={isLoading}
              required
            />
          </div>

          <div style={styles.formGroup}>
            <label htmlFor="passwordConfirm">Confirm Password</label>
            <input
              id="passwordConfirm"
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="Confirm password"
              disabled={isLoading}
              required
            />
          </div>

          {(error || authError) && (
            <div style={styles.error}>{error || authError}</div>
          )}

          <button type="submit" disabled={isLoading} style={styles.submitBtn}>
            {isLoading ? "Creating..." : "Create Account"}
          </button>
        </form>

        <p style={styles.link}>
          Already have an account?{" "}
          <Link href="/auth/login">Login here</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "calc(100vh - 70px)",
    padding: "20px",
  },
  formContainer: {
    width: "100%",
    maxWidth: "400px",
    padding: "40px",
    backgroundColor: "#f5f5f5",
    borderRadius: "8px",
  },
  formGroup: {
    marginBottom: "16px",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginTop: "6px",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    fontSize: "1rem",
    fontFamily: "inherit",
  },
  error: {
    color: "#dc2626",
    padding: "10px",
    backgroundColor: "#fee2e2",
    borderRadius: "4px",
    marginBottom: "16px",
  },
  submitBtn: {
    width: "100%",
    padding: "12px",
    backgroundColor: "#000",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "1rem",
    minHeight: "44px",
  },
  link: {
    textAlign: "center" as const,
    marginTop: "20px",
    color: "#666",
  },
};
