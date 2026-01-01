/**
 * Custom hook for authentication
 */

import { useAuth } from "../context/AuthContext";

export const useAuthHook = () => {
  return useAuth();
};
