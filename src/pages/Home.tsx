import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { BookOpen, Clock, Folder, TrendingUp, Plus, User as UserIcon, Shield, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SearchBar } from '@/components/SearchBar';
import { ArticleCard } from '@/components/ArticleCard';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useArticles } from '@/hooks/useArticles';
import type { Article, User as UserType } from '@/types';

interface HomeProps {
  user: UserType | null;
  isAdmin: boolean;
}

export function Home({ user, isAdmin }: HomeProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { articles, getRecent, getCategories, isLoading } = useArticles();
  const [recentArticles, setRecentArticles] = useState<Article[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const showPending = searchParams.get('pending') === 'true';

  useEffect(() => {
    // Filter only approved articles for display
    setRecentArticles(getRecent(6).filter(a => a.status === 'approved'));
    setCategories(getCategories());
  }, [getRecent, getCategories, articles]);

  const handleArticleSelect = (article: Article) => {
    navigate(`/article/${article.id}`);
  };

  const approvedArticlesList = articles.filter(a => a.status === 'approved');

  return (
    <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#202122]">
      {/* Hero Section */}
      <section className="bg-white dark:bg-[#202122] border-b border-[#A2A9B1] dark:border-[#3A4048] py-10 md:py-12">
        <div className="max-w-[1080px] mx-auto px-4 text-left">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="w-8 h-8 text-[#3366CC]" />
            <span className="text-sm uppercase tracking-wide text-[#54595D] dark:text-[#A2A9B1]">Свободная энциклопедия</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-[#202122] dark:text-[#F8F9FA] mb-3">
            Добро пожаловать в WalzerWiki
          </h1>
          <p className="text-lg text-[#54595D] dark:text-[#C8CCD1] mb-6 max-w-3xl">
            База знаний сообщества. Создавайте статьи, делитесь знаниями, отслеживайте изменения.
          </p>
          <div className="mb-6 max-w-2xl">
            <SearchBar 
              onSelect={handleArticleSelect}
              placeholder="Поиск по статьям..."
              autoFocus
            />
          </div>
          {user ? (
            <Button
              onClick={() => navigate('/edit')}
              className="bg-[#3366CC] hover:bg-[#2A56B0]"
            >
              <Plus className="w-4 h-4 mr-2" />
              Создать статью
            </Button>
          ) : (
            <p className="text-sm text-[#54595D] dark:text-[#C8CCD1]">
              <Button variant="link" onClick={() => navigate('/')} className="text-[#3366CC]">
                Войдите
              </Button>
              {' '}или{' '}
              <Button variant="link" onClick={() => navigate('/')} className="text-[#3366CC]">
                зарегистрируйтесь
              </Button>
              {' '}чтобы создавать статьи
            </p>
          )}
        </div>
      </section>

      {/* Pending Notice */}
      {showPending && (
        <section className="max-w-[1080px] mx-auto px-4 pt-8">
          <Alert className="bg-[#00AF89]/10 border-[#00AF89]/30">
            <CheckCircle className="w-4 h-4 text-[#00AF89]" />
            <AlertDescription className="text-[#00AF89]">
              Ваша статья отправлена на модерацию. После одобрения администратором она появится на сайте.
            </AlertDescription>
          </Alert>
        </section>
      )}

      {/* Main Content */}
      <section className="max-w-[1080px] mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Articles Column */}
          <div className="lg:col-span-8 space-y-6">
            {/* Recent Articles */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-[#202122] dark:text-white font-serif flex items-center gap-2">
                  <Clock className="w-5 h-5 text-[#72777D]" />
                  Недавние изменения
                </h2>
              </div>
              
              {isLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-32 bg-[#C8CCD1]/30 rounded-md animate-pulse" />
                  ))}
                </div>
              ) : recentArticles.length > 0 ? (
                <div className="space-y-4">
                  {recentArticles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-white dark:bg-[#2A2F36] rounded-lg border border-[#C8CCD1] dark:border-[#3A4048]">
                  <BookOpen className="w-12 h-12 text-[#C8CCD1] mx-auto mb-4" />
                  <p className="text-[#54595D] dark:text-[#C8CCD1]">Пока нет статей</p>
                  {user && (
                    <Button
                      onClick={() => navigate('/edit')}
                      variant="outline"
                      className="mt-4"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Создать первую статью
                    </Button>
                  )}
                </div>
              )}
            </div>

            {/* All Articles */}
            {approvedArticlesList.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-[#202122] dark:text-white font-serif mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-[#72777D]" />
                  Все статьи
                </h2>
                <div className="space-y-4">
                  {approvedArticlesList.slice(0, 10).map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            {/* Categories */}
            <div className="bg-white dark:bg-[#2A2F36] border border-[#C8CCD1] dark:border-[#3A4048] rounded-md p-4">
              <h3 className="font-semibold text-[#202122] dark:text-white mb-3 flex items-center gap-2">
                <Folder className="w-4 h-4 text-[#72777D]" />
                Категории
              </h3>
              {categories.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() => navigate(`/?category=${encodeURIComponent(category)}`)}
                      className="px-3 py-1 text-sm bg-[#F8F9FA] dark:bg-[#1a1a1a] hover:bg-[#3366CC]/10 text-[#3366CC] rounded-full transition-colors"
                    >
                      {category}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-[#54595D] dark:text-[#C8CCD1]">Пока нет категорий</p>
              )}
            </div>

            {/* Stats */}
            <div className="bg-white dark:bg-[#2A2F36] border border-[#C8CCD1] dark:border-[#3A4048] rounded-md p-4">
              <h3 className="font-semibold text-[#202122] dark:text-white mb-3">Статистика</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-[#54595D] dark:text-[#C8CCD1]">Всего статей:</span>
                  <span className="font-medium">{approvedArticlesList.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[#54595D] dark:text-[#C8CCD1]">Категорий:</span>
                  <span className="font-medium">{categories.length}</span>
                </div>
              </div>
            </div>

            {/* User Info */}
            {user && (
              <div className="bg-white dark:bg-[#2A2F36] border border-[#C8CCD1] dark:border-[#3A4048] rounded-md p-4">
                <h3 className="font-semibold text-[#202122] dark:text-white mb-3 flex items-center gap-2">
                  <UserIcon className="w-4 h-4 text-[#72777D]" />
                  Вы вошли как
                </h3>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#3366CC]/10 rounded-full flex items-center justify-center">
                    <UserIcon className="w-5 h-5 text-[#3366CC]" />
                  </div>
                  <div>
                    <p className="font-medium">{user.username}</p>
                    <p className="text-sm text-[#54595D] dark:text-[#C8CCD1]">
                      {isAdmin ? (
                        <span className="flex items-center gap-1">
                          <Shield className="w-3 h-3 text-[#3366CC]" />
                          Администратор
                        </span>
                      ) : 'Пользователь'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Info */}
            <div className="bg-[#F8F9FA] dark:bg-[#2A2F36] border border-[#C8CCD1] dark:border-[#3A4048] rounded-md p-4">
              <h3 className="font-semibold text-[#202122] dark:text-white mb-2">О проекте</h3>
              <p className="text-sm text-[#54595D] dark:text-[#C8CCD1]">
                WalzerWiki — платформа для создания и управления базой знаний. 
                Каждый пользователь имеет свой аккаунт с историей изменений.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
