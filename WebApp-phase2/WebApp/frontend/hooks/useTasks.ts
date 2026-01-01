/**
 * Custom hook for task management
 */

import { useTasks } from "../context/TaskContext";

export const useTasksHook = () => {
  return useTasks();
};
