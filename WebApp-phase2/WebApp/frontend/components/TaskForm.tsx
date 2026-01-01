"use client";

import React, { useState } from "react";
import { useTasks } from "../context/TaskContext";

interface TaskFormProps {
  onTaskCreated?: () => void;
}

export const TaskForm: React.FC<TaskFormProps> = ({ onTaskCreated }) => {
  const { createTask, isLoading, error } = useTasks();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [formError, setFormError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");

    if (!title.trim()) {
      setFormError("Title is required");
      return;
    }

    try {
      await createTask(title, description);
      setTitle("");
      setDescription("");
      onTaskCreated?.();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create task");
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h2>Add New Task</h2>

      <div style={styles.formGroup}>
        <label htmlFor="title">Title *</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          maxLength={255}
          style={styles.input}
          disabled={isLoading}
        />
        <span style={styles.charCount}>{title.length}/255</span>
      </div>

      <div style={styles.formGroup}>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description (optional)"
          maxLength={10000}
          style={styles.textarea}
          disabled={isLoading}
        />
      </div>

      {(formError || error) && (
        <div style={styles.error}>{formError || error}</div>
      )}

      <button
        type="submit"
        disabled={isLoading || !title.trim()}
        style={styles.submitBtn}
      >
        {isLoading ? "Adding..." : "Add Task"}
      </button>
    </form>
  );
};

const styles = {
  form: {
    backgroundColor: "#f5f5f5",
    padding: "20px",
    borderRadius: "8px",
    marginBottom: "24px",
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
  textarea: {
    width: "100%",
    padding: "10px",
    marginTop: "6px",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    minHeight: "100px",
    fontSize: "1rem",
    fontFamily: "inherit",
  },
  charCount: {
    fontSize: "0.75rem",
    color: "#999",
    marginTop: "4px",
    display: "block",
  },
  submitBtn: {
    padding: "12px 24px",
    backgroundColor: "#000",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "1rem",
    minWidth: "120px",
  },
  error: {
    color: "#dc2626",
    padding: "10px",
    backgroundColor: "#fee2e2",
    borderRadius: "4px",
    marginBottom: "16px",
  },
};
