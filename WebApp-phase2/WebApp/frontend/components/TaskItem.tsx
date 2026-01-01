"use client";

import React, { useState } from "react";
import { Task } from "../types/task";
import { useTasks } from "../context/TaskContext";

interface TaskItemProps {
  task: Task;
  onDelete?: (id: number) => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({ task, onDelete }) => {
  const { updateTask } = useTasks();
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description);

  const handleToggleComplete = async () => {
    await updateTask(task.id, { is_completed: !task.is_completed });
  };

  const handleSaveEdit = async () => {
    await updateTask(task.id, {
      title: editTitle,
      description: editDescription,
    });
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div style={styles.card}>
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          style={styles.input}
        />
        <textarea
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          style={styles.textarea}
        />
        <div style={styles.buttonGroup}>
          <button onClick={handleSaveEdit} style={styles.saveBtn}>
            Save
          </button>
          <button
            onClick={() => {
              setIsEditing(false);
              setEditTitle(task.title);
              setEditDescription(task.description);
            }}
            style={styles.cancelBtn}
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        ...styles.card,
        opacity: task.is_completed ? 0.6 : 1,
      }}
    >
      <div style={styles.taskContent}>
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggleComplete}
          style={styles.checkbox}
        />
        <div style={styles.textContent}>
          <h3
            style={{
              ...styles.title,
              textDecoration: task.is_completed ? "line-through" : "none",
            }}
          >
            {task.title}
          </h3>
          {task.description && (
            <p style={styles.description}>{task.description}</p>
          )}
          <span style={styles.date}>
            {new Date(task.created_at).toLocaleDateString()}
          </span>
        </div>
        <div style={styles.actions}>
          <button onClick={() => setIsEditing(true)} style={styles.editBtn}>
            Edit
          </button>
          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              style={styles.deleteBtn}
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  card: {
    border: "1px solid #e0e0e0",
    borderRadius: "8px",
    padding: "16px",
    marginBottom: "12px",
    backgroundColor: "#fff",
  },
  taskContent: {
    display: "flex",
    gap: "12px",
    alignItems: "flex-start",
  },
  checkbox: {
    marginTop: "4px",
    cursor: "pointer",
  },
  textContent: {
    flex: 1,
  },
  title: {
    margin: "0 0 8px 0",
    fontSize: "1rem",
  },
  description: {
    color: "#666",
    margin: "8px 0",
    fontSize: "0.875rem",
  },
  date: {
    color: "#999",
    fontSize: "0.75rem",
  },
  actions: {
    display: "flex",
    gap: "8px",
  },
  editBtn: {
    padding: "6px 12px",
    fontSize: "0.875rem",
    backgroundColor: "#000",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  deleteBtn: {
    padding: "6px 12px",
    fontSize: "0.875rem",
    backgroundColor: "#dc2626",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  cancelBtn: {
    padding: "8px 16px",
    backgroundColor: "transparent",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    cursor: "pointer",
  },
  saveBtn: {
    padding: "8px 16px",
    backgroundColor: "#10b981",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  input: {
    width: "100%",
    padding: "8px",
    marginBottom: "8px",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    fontSize: "1rem",
  },
  textarea: {
    width: "100%",
    padding: "8px",
    marginBottom: "8px",
    border: "1px solid #e0e0e0",
    borderRadius: "4px",
    minHeight: "80px",
  },
  buttonGroup: {
    display: "flex",
    gap: "8px",
  },
};
