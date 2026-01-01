"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { useTasks } from "../../context/TaskContext";
import { TaskForm } from "../../components/TaskForm";
import { TaskList } from "../../components/TaskList";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { tasks, isLoading, error, fetchTasks, deleteTask } = useTasks();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);

  // Fetch tasks on mount and when authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      fetchTasks();
    }
  }, [isAuthenticated, authLoading]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, authLoading, router]);

  const handleDeleteTask = async (taskId: number) => {
    setShowDeleteConfirm(taskId);
  };

  const confirmDelete = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      setShowDeleteConfirm(null);
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  if (authLoading || (!isAuthenticated && authLoading)) {
    return <div style={styles.loading}>Loading...</div>;
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="container" style={styles.container}>
      <h1>My Tasks</h1>

      <TaskForm onTaskCreated={() => fetchTasks()} />

      {error && <div style={styles.error}>{error}</div>}

      {isLoading ? (
        <div style={styles.loading}>Loading tasks...</div>
      ) : (
        <>
          <TaskList tasks={tasks} onDeleteTask={handleDeleteTask} />

          {showDeleteConfirm !== null && (
            <div style={styles.confirmDialog}>
              <div style={styles.dialogContent}>
                <p>Are you sure you want to delete this task?</p>
                <div style={styles.dialogButtons}>
                  <button
                    onClick={() => confirmDelete(showDeleteConfirm)}
                    style={styles.confirmBtn}
                  >
                    Delete
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(null)}
                    style={styles.cancelBtn}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: "24px",
    maxWidth: "800px",
  },
  error: {
    color: "#dc2626",
    padding: "12px",
    backgroundColor: "#fee2e2",
    borderRadius: "4px",
    marginBottom: "16px",
  },
  loading: {
    textAlign: "center" as const,
    padding: "40px",
    color: "#666",
  },
  confirmDialog: {
    position: "fixed" as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  dialogContent: {
    backgroundColor: "#fff",
    padding: "24px",
    borderRadius: "8px",
    maxWidth: "400px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
  },
  dialogButtons: {
    display: "flex",
    gap: "12px",
    marginTop: "16px",
    justifyContent: "flex-end",
  },
  confirmBtn: {
    padding: "8px 16px",
    backgroundColor: "#dc2626",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  cancelBtn: {
    padding: "8px 16px",
    backgroundColor: "#f5f5f5",
    color: "#000",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    cursor: "pointer",
  },
};
