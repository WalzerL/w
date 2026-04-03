import { useState, useEffect, useCallback } from 'react';
import type { User } from '@/types';
import { 
  getCurrentUser, 
  setCurrentUser, 
  verifyPassword,
  verifyUserCredentials,
  getUsers,
  saveUser,
  deleteUser,
  getUserByUsername
} from '@/utils/storage';
import { sha256, generateId } from '@/utils/crypto';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    setIsLoading(false);
  }, []);

  // Login with username and password
  const login = useCallback(async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
    const authenticatedUser = await verifyUserCredentials(username, password);
    if (authenticatedUser) {
      setCurrentUser(authenticatedUser);
      setUser(authenticatedUser);
      return { success: true };
    }
    return { success: false, error: 'Неверное имя пользователя или пароль' };
  }, []);

  // Legacy login with just password (for admin)
  const loginWithPassword = useCallback(async (password: string): Promise<boolean> => {
    const authenticatedUser = await verifyPassword(password);
    if (authenticatedUser) {
      setCurrentUser(authenticatedUser);
      setUser(authenticatedUser);
      return true;
    }
    return false;
  }, []);

  // Register new user
  const register = useCallback(async (
    username: string, 
    password: string, 
    email?: string
  ): Promise<{ success: boolean; error?: string }> => {
    // Check if username already exists
    const existingUser = getUserByUsername(username);
    if (existingUser) {
      return { success: false, error: 'Пользователь с таким именем уже существует' };
    }

    // Check username length
    if (username.length < 3) {
      return { success: false, error: 'Имя пользователя должно быть не менее 3 символов' };
    }

    // Check password strength
    if (password.length < 6) {
      return { success: false, error: 'Пароль должен быть не менее 6 символов' };
    }

    try {
      const passwordHash = await sha256(password);
      const newUser: User = {
        id: generateId(),
        username,
        email,
        isAdmin: false, // New users are not admins by default
        passwordHash,
        createdAt: Date.now(),
      };
      saveUser(newUser);
      
      // Auto-login after registration
      setCurrentUser(newUser);
      setUser(newUser);
      
      return { success: true };
    } catch {
      return { success: false, error: 'Ошибка при создании пользователя' };
    }
  }, []);

  const logout = useCallback(() => {
    setCurrentUser(null);
    setUser(null);
  }, []);

  const isAdmin = useCallback(() => {
    return user?.isAdmin === true;
  }, [user]);

  const createUser = useCallback(async (
    username: string, 
    password: string, 
    isAdmin: boolean = false,
    email?: string
  ): Promise<{ user?: User; error?: string }> => {
    // Check if username already exists
    const existingUser = getUserByUsername(username);
    if (existingUser) {
      return { error: 'Пользователь с таким именем уже существует' };
    }

    try {
      const passwordHash = await sha256(password);
      const newUser: User = {
        id: generateId(),
        username,
        email,
        isAdmin,
        passwordHash,
        createdAt: Date.now(),
      };
      saveUser(newUser);
      return { user: newUser };
    } catch {
      return { error: 'Ошибка при создании пользователя' };
    }
  }, []);

  const updateUser = useCallback(async (
    userId: string, 
    updates: Partial<User> & { password?: string }
  ): Promise<User | null> => {
    const users = getUsers();
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) return null;
    
    const updatedUser = { ...users[userIndex] };
    
    if (updates.username) updatedUser.username = updates.username;
    if (updates.email !== undefined) updatedUser.email = updates.email;
    if (updates.isAdmin !== undefined) updatedUser.isAdmin = updates.isAdmin;
    if (updates.password) {
      updatedUser.passwordHash = await sha256(updates.password);
    }
    
    saveUser(updatedUser);
    
    // Update current user if it's the same user
    if (user?.id === userId) {
      setCurrentUser(updatedUser);
      setUser(updatedUser);
    }
    
    return updatedUser;
  }, [user]);

  const removeUser = useCallback((userId: string): { success: boolean; error?: string } => {
    // Prevent deleting the last admin
    const users = getUsers();
    const adminCount = users.filter(u => u.isAdmin).length;
    const targetUser = users.find(u => u.id === userId);
    
    if (targetUser?.isAdmin && adminCount <= 1) {
      return { success: false, error: 'Нельзя удалить последнего администратора' };
    }
    
    deleteUser(userId);
    
    // Logout if deleting current user
    if (user?.id === userId) {
      logout();
    }
    
    return { success: true };
  }, [user, logout]);

  const getAllUsers = useCallback(() => {
    return getUsers();
  }, []);

  const canEditArticle = useCallback((articleAuthorId: string): boolean => {
    if (!user) return false;
    if (user.isAdmin) return true;
    return user.id === articleAuthorId;
  }, [user]);

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    isAdmin: isAdmin(),
    login,
    loginWithPassword,
    register,
    logout,
    createUser,
    updateUser,
    removeUser,
    getAllUsers,
    canEditArticle,
  };
}
