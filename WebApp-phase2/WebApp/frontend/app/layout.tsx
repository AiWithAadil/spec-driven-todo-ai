import React from "react";
import { AuthProvider } from "../context/AuthContext";
import { TaskProvider } from "../context/TaskContext";
import { Header } from "../components/Header";
import "../styles/globals.css";

export const metadata = {
  title: "Todo App",
  description: "A simple and clean todo application",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <TaskProvider>
            <Header />
            <main style={{ minHeight: "calc(100vh - 70px)" }}>
              {children}
            </main>
          </TaskProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
