/**
 * Task service for API calls
 */

import { apiClient } from "./api";
import { Task, TaskListResponse, TaskUpdateRequest } from "../types/task";

export const taskService = {
  fetchTasks: async (): Promise<Task[]> => {
    const response = await apiClient.get<TaskListResponse>("/api/v1/tasks");
    return response.tasks;
  },

  createTask: async (title: string, description: string = ""): Promise<Task> => {
    const response = await apiClient.post<Task>("/api/v1/tasks", {
      title,
      description,
    });
    return response;
  },

  getTask: async (id: number): Promise<Task> => {
    const response = await apiClient.get<Task>(`/api/v1/tasks/${id}`);
    return response;
  },

  updateTask: async (id: number, data: TaskUpdateRequest): Promise<Task> => {
    const response = await apiClient.put<Task>(`/api/v1/tasks/${id}`, data);
    return response;
  },

  partialUpdateTask: async (id: number, data: TaskUpdateRequest): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/api/v1/tasks/${id}`, data);
    return response;
  },

  deleteTask: async (id: number): Promise<void> => {
    await apiClient.delete<void>(`/api/v1/tasks/${id}`);
  },
};
