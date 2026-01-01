/**
 * Task related types
 */

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface TaskContextType {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (title: string, description?: string) => Promise<void>;
  updateTask: (id: number, data: TaskUpdateRequest) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
}
