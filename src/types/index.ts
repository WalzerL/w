// Types for WalzerWiki application

export interface Article {
  id: string;
  title: string;
  content: string;
  category: string;
  createdAt: number;
  updatedAt: number;
  author: string;
  authorId: string;
  isProtected: boolean;
  status: 'pending' | 'approved' | 'rejected';
  changelog: ChangelogEntry[];
}

export interface ChangelogEntry {
  id: string;
  timestamp: number;
  userId: string;
  username: string;
  changes: string[];
  type: 'create' | 'edit' | 'delete' | 'restore';
}

export interface User {
  id: string;
  username: string;
  email?: string;
  isAdmin: boolean;
  passwordHash: string;
  passwordSalt?: string;
  passwordAlgo?: 'sha256' | 'pbkdf2';
  createdAt: number;
  avatar?: string;
}

export interface SiteSettings {
  siteName: string;
  siteDescription: string;
  logoUrl?: string;
  allowRegistration: boolean;
  darkMode: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
}

export interface SearchResult {
  article: Article;
  relevance: number;
}

export interface UploadedFile {
  id: string;
  name: string;
  type: string;
  data: string;
  uploadedAt: number;
  uploadedBy: string;
}
