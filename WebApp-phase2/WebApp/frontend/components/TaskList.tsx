"use client";

import React from "react";
import { Task } from "../types/task";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  onDeleteTask: (id: number) => void;
}

export const TaskList: React.FC<TaskListProps> = ({ tasks, onDeleteTask }) => {
  return (
    <div>
      {tasks.length === 0 ? (
        <div style={styles.emptyState}>
          <p>No tasks yet. Create one to get started!</p>
        </div>
      ) : (
        <ul style={styles.list}>
          {tasks.map((task) => (
            <li key={task.id}>
              <TaskItem task={task} onDelete={onDeleteTask} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const styles = {
  list: {
    listStyle: "none",
    padding: 0,
  },
  emptyState: {
    textAlign: "center" as const,
    padding: "40px 20px",
    color: "#999",
    fontSize: "1.125rem",
  },
};
