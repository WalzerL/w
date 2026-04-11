import { useState, useEffect, useCallback } from 'react';
import type { User } from '@/types';
import {
  getCurrentUser,
  setCurrentUser,
  verifyUserCredentials,
  getUsers,
  saveUser,
  deleteUser,
  getUserByUsername
} from '@/utils/storage';
import { generateId, generateSalt, hashPassword, validatePasswordStrength } from '@/utils/crypto';

const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_MS = 5 * 60 * 1000;

type AttemptRecord = {
  count: number;
  lockedUntil: number;
};

const loginAttempts = new Map<string, AttemptRecord>();

function getAttemptState(username: string): AttemptRecord {
  const key = username.toLowerCase();
  return loginAttempts.get(key) ?? { count: 0, lockedUntil: 0 };
}

function setAttemptState(username: string, state: AttemptRecord): void {
  loginAttempts.set(username.toLowerCase(), state);
}

function resetAttemptState(username: string): void {
  loginAttempts.delete(username.toLowerCase());
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    setIsLoading(false);
  }, []);

  const login = useCallback(async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
    const normalizedUsername = username.trim();
    const attemptState = getAttemptState(normalizedUsername);

    if (attemptState.lockedUntil > Date.now()) {
      const secondsLeft = Math.ceil((attemptState.lockedUntil - Date.now()) / 1000);
      return {
        success: false,
        error: `Слишком много попыток входа. Повторите через ${secondsLeft} сек.`,
      };
    }

    const authenticatedUser = await verifyUserCredentials(normalizedUsername, password);
    if (authenticatedUser) {
      resetAttemptState(normalizedUsername);
      setCurrentUser(authenticatedUser);
      setUser(authenticatedUser);
      return { success: true };
    }

    const nextAttempts = attemptState.count + 1;
    const shouldLock = nextAttempts >= MAX_LOGIN_ATTEMPTS;
    setAttemptState(normalizedUsername, {
      count: shouldLock ? 0 : nextAttempts,
      lockedUntil: shouldLock ? Date.now() + LOCKOUT_MS : 0,
    });

    return { success: false, error: 'Неверное имя пользователя или пароль' };
  }, []);

  const register = useCallback(async (
    username: string,
    password: string,
    email?: string
  ): Promise<{ success: boolean; error?: string }> => {
    const normalizedUsername = username.trim();

    const existingUser = getUserByUsername(normalizedUsername);
    if (existingUser) {
      return { success: false, error: 'Пользователь с таким именем уже существует' };
    }

    if (normalizedUsername.length < 3) {
      return { success: false, error: 'Имя пользователя должно быть не менее 3 символов' };
    }

    const passwordError = validatePasswordStrength(password);
    if (passwordError) {
      return { success: false, error: passwordError };
    }

    try {
      const passwordSalt = generateSalt();
      const passwordHash = await hashPassword(password, passwordSalt);
      const newUser: User = {
        id: generateId(),
        username: normalizedUsername,
        email,
        isAdmin: false,
        passwordHash,
        passwordSalt,
        passwordAlgo: 'pbkdf2',
        createdAt: Date.now(),
      };
      saveUser(newUser);

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
    const normalizedUsername = username.trim();

    const existingUser = getUserByUsername(normalizedUsername);
    if (existingUser) {
      return { error: 'Пользователь с таким именем уже существует' };
    }

    const passwordError = validatePasswordStrength(password);
    if (passwordError) {
      return { error: passwordError };
    }

    try {
      const passwordSalt = generateSalt();
      const passwordHash = await hashPassword(password, passwordSalt);
      const newUser: User = {
        id: generateId(),
        username: normalizedUsername,
        email,
        isAdmin,
        passwordHash,
        passwordSalt,
        passwordAlgo: 'pbkdf2',
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

    if (updates.username) updatedUser.username = updates.username.trim();
    if (updates.email !== undefined) updatedUser.email = updates.email;
    if (updates.isAdmin !== undefined) updatedUser.isAdmin = updates.isAdmin;
    if (updates.password) {
      const passwordError = validatePasswordStrength(updates.password);
      if (passwordError) {
        return null;
      }
      const passwordSalt = generateSalt();
      updatedUser.passwordHash = await hashPassword(updates.password, passwordSalt);
      updatedUser.passwordSalt = passwordSalt;
      updatedUser.passwordAlgo = 'pbkdf2';
    }

    saveUser(updatedUser);

    if (user?.id === userId) {
      setCurrentUser(updatedUser);
      setUser(updatedUser);
    }

    return updatedUser;
  }, [user]);

  const removeUser = useCallback((userId: string): { success: boolean; error?: string } => {
    const users = getUsers();
    const adminCount = users.filter(u => u.isAdmin).length;
    const targetUser = users.find(u => u.id === userId);

    if (targetUser?.isAdmin && adminCount <= 1) {
      return { success: false, error: 'Нельзя удалить последнего администратора' };
    }

    deleteUser(userId);

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
    register,
    logout,
    createUser,
    updateUser,
    removeUser,
    getAllUsers,
    canEditArticle,
  };
}
