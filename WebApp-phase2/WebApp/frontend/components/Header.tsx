"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";

export const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header style={styles.header}>
      <div className="container" style={styles.container}>
        <Link href="/" style={styles.logo}>
          <h1>Todo App</h1>
        </Link>
        <nav style={styles.nav}>
          {user ? (
            <>
              <span style={styles.email}>{user.email}</span>
              <button onClick={logout} style={styles.logoutBtn}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/auth/login">
                <button>Login</button>
              </Link>
              <Link href="/auth/register">
                <button>Register</button>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

const styles = {
  header: {
    backgroundColor: "#f5f5f5",
    borderBottom: "1px solid #e0e0e0",
    padding: "16px 0",
  },
  container: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  logo: {
    textDecoration: "none",
    color: "inherit",
  },
  nav: {
    display: "flex",
    gap: "16px",
    alignItems: "center",
  },
  email: {
    color: "#666",
  },
  logoutBtn: {
    backgroundColor: "transparent",
    color: "#1a1a1a",
    border: "1px solid #e0e0e0",
    cursor: "pointer",
    padding: "8px 16px",
    borderRadius: "4px",
  },
};
