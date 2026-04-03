// LocalStorage management utilities

import type { Article, User, SiteSettings, UploadedFile } from '@/types';

const STORAGE_KEYS = {
  ARTICLES: 'walzerwiki_articles',
  USERS: 'walzerwiki_users',
  SETTINGS: 'walzerwiki_settings',
  CURRENT_USER: 'walzerwiki_current_user',
  FILES: 'walzerwiki_files',
};

// Hash for password: мамаденисажирнаясвинотахрюхрюБЛЯ123
const ADMIN_PASSWORD_HASH = 'zalupka'; // SHA-256 hash

// Admin users
const DEFAULT_ADMINS: User[] = [
  {
    id: 'admin_uofist',
    username: 'uofist',
    email: 'uofist@walzerwiki.local',
    isAdmin: true,
    passwordHash: ADMIN_PASSWORD_HASH,
    createdAt: new Date('2025-04-03').getTime(),
  },
  {
    id: 'admin_lemonov',
    username: 'lemonov',
    email: 'lemonov@walzerwiki.local',
    isAdmin: true,
    passwordHash: ADMIN_PASSWORD_HASH,
    createdAt: new Date('2025-04-03').getTime(),
  },
];

const DEFAULT_SETTINGS: SiteSettings = {
  siteName: 'WalzerWiki',
  siteDescription: 'База знаний сообщества',
  allowRegistration: true,
  darkMode: false,
};

// Demo articles for first load (all approved by default)
const DEMO_ARTICLES: Article[] = [
  {
    id: 'article_1',
    title: 'Добро пожаловать в WalzerWiki',
    content: `# Добро пожаловать в WalzerWiki

WalzerWiki — это платформа для создания и управления базой знаний сообщества.

## Основные возможности

- **Создание статей** — пишите статьи с поддержкой Markdown
- **Управление пользователями** — каждый имеет свой аккаунт
- **История изменений** — отслеживайте все правки
- **Категории** — организуйте статьи по темам
- **Поиск** — быстрый поиск по всем статьям
- **Медиа** — загружайте изображения и файлы

## Как начать

1. Зарегистрируйтесь или войдите в аккаунт
2. Создайте новую статью через кнопку "Создать"
3. Используйте Markdown для форматирования
4. Загружайте изображения прямо в редактор
5. Сохраните и публикуйте

## Безопасность

Все пароли хранятся в зашифрованном виде (SHA-256). Данные сохраняются локально в браузере.`,
    category: 'Инструкции',
    createdAt: new Date('2025-04-03').getTime(),
    updatedAt: new Date('2025-04-03').getTime(),
    author: 'uofist',
    authorId: 'admin_uofist',
    isProtected: true,
    status: 'approved',
    changelog: [
      {
        id: 'chg_1',
        timestamp: new Date('2025-04-03').getTime(),
        userId: 'admin_uofist',
        username: 'uofist',
        changes: ['Создание статьи'],
        type: 'create'
      }
    ]
  },
  {
    id: 'article_2',
    title: 'Руководство по Markdown',
    content: `# Руководство по Markdown

Markdown — это простой язык разметки для форматирования текста.

## Заголовки

\`\`\`markdown
# Заголовок 1
## Заголовок 2
### Заголовок 3
\`\`\`

## Текст

- **Жирный текст** — \`**текст**\`
- *Курсив* — \`*текст*\`
- ~~Зачеркнутый~~ — \`~~текст~~\`

## Списки

Ненумерованный список:
- Пункт 1
- Пункт 2
  - Подпункт

Нумерованный список:
1. Первый
2. Второй

## Ссылки и изображения

[Текст ссылки](https://example.com)

![Описание изображения](/path/to/image.png)

## Код

Встроенный код: \`const x = 1\`

Блок кода:
\`\`\`javascript
function hello() {
  console.log('Hello!');
}
\`\`\`

## Цитаты

> Это цитата
> на несколько строк

## Таблицы

| Заголовок 1 | Заголовок 2 |
|-------------|-------------|
| Ячейка 1    | Ячейка 2    |
| Ячейка 3    | Ячейка 4    |`,
    category: 'Инструкции',
    createdAt: new Date('2025-04-03').getTime(),
    updatedAt: new Date('2025-04-03').getTime(),
    author: 'lemonov',
    authorId: 'admin_lemonov',
    isProtected: false,
    status: 'approved',
    changelog: [
      {
        id: 'chg_2',
        timestamp: new Date('2025-04-03').getTime(),
        userId: 'admin_lemonov',
        username: 'lemonov',
        changes: ['Создание статьи'],
        type: 'create'
      }
    ]
  },
  {
    id: 'article_3',
    title: 'Система пользователей и прав доступа',
    content: `# Система пользователей и прав доступа

WalzerWiki использует систему аутентификации с индивидуальными аккаунтами.

## Регистрация

Каждый пользователь может создать свой аккаунт:

1. Нажмите "Войти" → "Регистрация"
2. Введите имя пользователя
3. Придумайте надежный пароль
4. Подтвердите регистрацию

## Типы пользователей

### Администраторы

Администраторы имеют полный доступ:

- Создание и редактирование любых статей
- Удаление статей
- Управление пользователями
- Модерация статей
- Защита статей от вандализма

### Обычные пользователи

- Создание статей (требуют модерации)
- Редактирование своих статей
- Просмотр всех одобренных статей
- Использование поиска
- Загрузка файлов

## История изменений

Каждое изменение статьи записывается:

- Кто изменил
- Когда изменил
- Что именно изменилось

## Безопасность

- Пароли хешируются с помощью SHA-256
- Пароли никогда не хранятся в открытом виде
- Данные хранятся локально в браузере`,
    category: 'Администрирование',
    createdAt: new Date('2025-04-03').getTime(),
    updatedAt: new Date('2025-04-03').getTime(),
    author: 'uofist',
    authorId: 'admin_uofist',
    isProtected: true,
    status: 'approved',
    changelog: [
      {
        id: 'chg_3',
        timestamp: new Date('2025-04-03').getTime(),
        userId: 'admin_uofist',
        username: 'uofist',
        changes: ['Создание статьи'],
        type: 'create'
      }
    ]
  },
  {
    id: 'article_4',
    title: 'Часто задаваемые вопросы',
    content: `# Часто задаваемые вопросы (FAQ)

## Как зарегистрироваться?

Нажмите "Войти" → "Регистрация" и заполните форму.

## Где хранятся данные?

Все данные хранятся локально в браузере с помощью localStorage.

## Можно ли использовать на GitHub Pages?

Да! Это статическое приложение, полностью совместимое с GitHub Pages.

## Как загрузить изображение?

В редакторе статьи нажмите кнопку загрузки файла или перетащите изображение.

## Кто может редактировать статьи?

- Администраторы — любые статьи
- Обычные пользователи — только свои статьи (до модерации)

## Что такое защищенные статьи?

Защищенные статьи могут редактировать только администраторы.

## Что такое модерация?

Статьи созданные обычными пользователями требуют одобрения администратора перед публикацией.`,
    category: 'Помощь',
    createdAt: new Date('2025-04-03').getTime(),
    updatedAt: new Date('2025-04-03').getTime(),
    author: 'lemonov',
    authorId: 'admin_lemonov',
    isProtected: false,
    status: 'approved',
    changelog: [
      {
        id: 'chg_4',
        timestamp: new Date('2025-04-03').getTime(),
        userId: 'admin_lemonov',
        username: 'lemonov',
        changes: ['Создание статьи'],
        type: 'create'
      }
    ]
  }
];

// Initialize storage with default data
export function initializeStorage(): void {
  if (!localStorage.getItem(STORAGE_KEYS.USERS)) {
    localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(DEFAULT_ADMINS));
  }
  if (!localStorage.getItem(STORAGE_KEYS.ARTICLES)) {
    localStorage.setItem(STORAGE_KEYS.ARTICLES, JSON.stringify(DEMO_ARTICLES));
  }
  if (!localStorage.getItem(STORAGE_KEYS.SETTINGS)) {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(DEFAULT_SETTINGS));
  }
  if (!localStorage.getItem(STORAGE_KEYS.FILES)) {
    localStorage.setItem(STORAGE_KEYS.FILES, JSON.stringify([]));
  }
}

// Articles
export function getArticles(): Article[] {
  const data = localStorage.getItem(STORAGE_KEYS.ARTICLES);
  return data ? JSON.parse(data) : [];
}

export function getApprovedArticles(): Article[] {
  return getArticles().filter(a => a.status === 'approved');
}

export function getPendingArticles(): Article[] {
  return getArticles().filter(a => a.status === 'pending');
}

export function getArticleById(id: string): Article | null {
  const articles = getArticles();
  return articles.find(a => a.id === id) || null;
}

export function saveArticle(article: Article): void {
  const articles = getArticles();
  const existingIndex = articles.findIndex(a => a.id === article.id);
  
  if (existingIndex >= 0) {
    articles[existingIndex] = article;
  } else {
    articles.push(article);
  }
  
  localStorage.setItem(STORAGE_KEYS.ARTICLES, JSON.stringify(articles));
}

export function deleteArticle(id: string): void {
  const articles = getArticles().filter(a => a.id !== id);
  localStorage.setItem(STORAGE_KEYS.ARTICLES, JSON.stringify(articles));
}

export function searchArticles(query: string): Article[] {
  const articles = getApprovedArticles();
  const lowerQuery = query.toLowerCase();
  
  return articles.filter(article => 
    article.title.toLowerCase().includes(lowerQuery) ||
    article.content.toLowerCase().includes(lowerQuery) ||
    article.category.toLowerCase().includes(lowerQuery)
  );
}

// Users
export function getUsers(): User[] {
  const data = localStorage.getItem(STORAGE_KEYS.USERS);
  return data ? JSON.parse(data) : [];
}

export function getUserById(id: string): User | null {
  const users = getUsers();
  return users.find(u => u.id === id) || null;
}

export function getUserByUsername(username: string): User | null {
  const users = getUsers();
  return users.find(u => u.username.toLowerCase() === username.toLowerCase()) || null;
}

export function saveUser(user: User): void {
  const users = getUsers();
  const existingIndex = users.findIndex(u => u.id === user.id);
  
  if (existingIndex >= 0) {
    users[existingIndex] = user;
  } else {
    users.push(user);
  }
  
  localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
}

export function deleteUser(id: string): void {
  const users = getUsers().filter(u => u.id !== id);
  localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
}

export async function verifyPassword(password: string): Promise<User | null> {
  const { sha256 } = await import('./crypto');
  const passwordHash = await sha256(password);
  const users = getUsers();
  return users.find(u => u.passwordHash === passwordHash) || null;
}

export async function verifyUserCredentials(username: string, password: string): Promise<User | null> {
  const { sha256 } = await import('./crypto');
  const passwordHash = await sha256(password);
  const users = getUsers();
  return users.find(u => 
    u.username.toLowerCase() === username.toLowerCase() && 
    u.passwordHash === passwordHash
  ) || null;
}

// Current session
export function getCurrentUser(): User | null {
  const data = localStorage.getItem(STORAGE_KEYS.CURRENT_USER);
  return data ? JSON.parse(data) : null;
}

export function setCurrentUser(user: User | null): void {
  if (user) {
    localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify(user));
  } else {
    localStorage.removeItem(STORAGE_KEYS.CURRENT_USER);
  }
}

// Settings
export function getSettings(): SiteSettings {
  const data = localStorage.getItem(STORAGE_KEYS.SETTINGS);
  return data ? JSON.parse(data) : DEFAULT_SETTINGS;
}

export function saveSettings(settings: SiteSettings): void {
  localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
}

// Files
export function getFiles(): UploadedFile[] {
  const data = localStorage.getItem(STORAGE_KEYS.FILES);
  return data ? JSON.parse(data) : [];
}

export function saveFile(file: UploadedFile): void {
  const files = getFiles();
  files.push(file);
  localStorage.setItem(STORAGE_KEYS.FILES, JSON.stringify(files));
}

export function deleteFile(id: string): void {
  const files = getFiles().filter(f => f.id !== id);
  localStorage.setItem(STORAGE_KEYS.FILES, JSON.stringify(files));
}

export function getFileById(id: string): UploadedFile | null {
  const files = getFiles();
  return files.find(f => f.id === id) || null;
}
