import { useState, useEffect, useCallback } from 'react';
import type { Article, ChangelogEntry, User } from '@/types';
import { 
  getArticles, 
  getArticleById, 
  saveArticle, 
  deleteArticle,
  searchArticles 
} from '@/utils/storage';
import { generateId } from '@/utils/crypto';

export function useArticles() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadedArticles = getArticles();
    setArticles(loadedArticles);
    setIsLoading(false);
  }, []);

  const getAll = useCallback(() => {
    return getArticles();
  }, []);

  const getById = useCallback((id: string) => {
    return getArticleById(id);
  }, []);

  // Detect changes between old and new content
  const detectChanges = (oldArticle: Article | null, newData: Partial<Article>): string[] => {
    const changes: string[] = [];
    
    if (!oldArticle) {
      return ['Создание статьи'];
    }

    if (newData.title !== undefined && newData.title !== oldArticle.title) {
      changes.push(`Изменен заголовок: "${oldArticle.title}" → "${newData.title}"`);
    }
    
    if (newData.category !== undefined && newData.category !== oldArticle.category) {
      changes.push(`Изменена категория: "${oldArticle.category}" → "${newData.category}"`);
    }
    
    if (newData.content !== undefined && newData.content !== oldArticle.content) {
      const oldLength = oldArticle.content.length;
      const newLength = newData.content.length;
      const diff = newLength - oldLength;
      
      if (diff > 0) {
        changes.push(`Добавлено ${diff} символов в содержание`);
      } else if (diff < 0) {
        changes.push(`Удалено ${Math.abs(diff)} символов из содержания`);
      } else {
        changes.push('Изменено содержание');
      }
    }
    
    if (newData.isProtected !== undefined && newData.isProtected !== oldArticle.isProtected) {
      changes.push(newData.isProtected ? 'Статья защищена' : 'Снята защита со статьи');
    }

    if (changes.length === 0) {
      changes.push('Минорные изменения');
    }

    return changes;
  };

  const create = useCallback((
    articleData: Omit<Article, 'id' | 'createdAt' | 'updatedAt' | 'changelog' | 'authorId'>,
    user: User
  ): Article => {
    const now = Date.now();
    const initialChangelog: ChangelogEntry = {
      id: generateId(),
      timestamp: now,
      userId: user.id,
      username: user.username,
      changes: ['Создание статьи'],
      type: 'create'
    };

    const newArticle: Article = {
      ...articleData,
      id: generateId(),
      authorId: user.id,
      createdAt: now,
      updatedAt: now,
      changelog: [initialChangelog],
    };
    saveArticle(newArticle);
    setArticles(prev => [...prev, newArticle]);
    return newArticle;
  }, []);

  const update = useCallback((
    id: string, 
    updates: Partial<Article>,
    user: User
  ): Article | null => {
    const existingArticle = getArticleById(id);
    if (!existingArticle) return null;

    // Detect what changed
    const changes = detectChanges(existingArticle, updates);

    // Create changelog entry
    const changelogEntry: ChangelogEntry = {
      id: generateId(),
      timestamp: Date.now(),
      userId: user.id,
      username: user.username,
      changes,
      type: 'edit'
    };

    const updatedArticle: Article = {
      ...existingArticle,
      ...updates,
      updatedAt: Date.now(),
      changelog: [...existingArticle.changelog, changelogEntry],
    };
    saveArticle(updatedArticle);
    setArticles(prev => prev.map(a => a.id === id ? updatedArticle : a));
    return updatedArticle;
  }, []);

  const remove = useCallback((id: string, _user: User): boolean => {
    const article = getArticleById(id);
    if (!article) return false;
    
    deleteArticle(id);
    setArticles(prev => prev.filter(a => a.id !== id));
    return true;
  }, []);

  const search = useCallback((query: string) => {
    return searchArticles(query);
  }, []);

  const getByCategory = useCallback((category: string) => {
    return getArticles().filter(a => a.category === category);
  }, []);

  const getCategories = useCallback(() => {
    const allArticles = getArticles();
    const categories = new Set(allArticles.map(a => a.category));
    return Array.from(categories).filter(Boolean).sort();
  }, []);

  const getRecent = useCallback((limit: number = 5) => {
    return getArticles()
      .sort((a, b) => b.updatedAt - a.updatedAt)
      .slice(0, limit);
  }, []);

  const getUserArticles = useCallback((userId: string) => {
    return getArticles().filter(a => a.authorId === userId);
  }, []);

  return {
    articles,
    isLoading,
    getAll,
    getById,
    create,
    update,
    remove,
    search,
    getByCategory,
    getCategories,
    getRecent,
    getUserArticles,
  };
}
