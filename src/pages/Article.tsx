import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Edit, 
  Trash2, 
  Clock, 
  User, 
  Folder, 
  ArrowLeft,
  AlertTriangle,
  Shield,
  History,
  Clock as ClockIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { TOC } from '@/components/TOC';
import { Changelog } from '@/components/Changelog';
import { useArticles } from '@/hooks/useArticles';
import { parseMarkdown, extractHeadings } from '@/utils/markdown';
import type { Article as ArticleType, User as UserType } from '@/types';

interface ArticlePageProps {
  user: UserType | null;
  isAdmin: boolean;
}

export function ArticlePage({ user, isAdmin }: ArticlePageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getById, remove } = useArticles();
  const [article, setArticle] = useState<ArticleType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (id) {
      const foundArticle = getById(id);
      // Check if article exists and is accessible
      if (foundArticle) {
        // Non-admins can only see approved articles
        if (!isAdmin && foundArticle.status !== 'approved') {
          setArticle(null);
        } else {
          setArticle(foundArticle);
        }
      } else {
        setArticle(null);
      }
      setIsLoading(false);
    }
  }, [id, getById, isAdmin]);

  const handleDelete = async () => {
    if (!article || !user) return;
    
    setIsDeleting(true);
    try {
      remove(article.id, user);
      navigate('/');
    } catch {
      setIsDeleting(false);
    }
  };

  const canEdit = (): boolean => {
    if (!user) return false;
    if (isAdmin) return true;
    if (article?.isProtected) return false;
    if (article?.status === 'pending') return article.authorId === user.id;
    return article?.authorId === user.id;
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
        <div className="max-w-[960px] mx-auto px-4">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-[#C8CCD1]/30 rounded w-3/4" />
            <div className="h-4 bg-[#C8CCD1]/30 rounded w-1/2" />
            <div className="h-64 bg-[#C8CCD1]/30 rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
        <div className="max-w-[960px] mx-auto px-4 text-center py-16">
          <AlertTriangle className="w-16 h-16 text-[#FFCC33] mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-[#202122] dark:text-white mb-2">Статья не найдена</h1>
          <p className="text-[#54595D] dark:text-[#aaa] mb-6">Запрашиваемая статья не существует или находится на модерации.</p>
          <Button onClick={() => navigate('/')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            На главную
          </Button>
        </div>
      </div>
    );
  }

  const headings = extractHeadings(article.content);
  const parsedContent = parseMarkdown(article.content);
  const lastEdit = article.changelog[article.changelog.length - 1];

  return (
    <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
      <div className="max-w-[960px] mx-auto px-4">
        {/* Back Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/')}
          className="mb-4 text-[#54595D] dark:text-[#aaa] hover:text-[#202122]"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <article className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md overflow-hidden">
              {/* Article Header */}
              <div className="p-6 border-b border-[#C8CCD1] dark:border-[#444]">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <h1 className="text-3xl font-bold text-[#202122] dark:text-white font-serif">
                    {article.title}
                  </h1>
                  <div className="flex gap-2">
                    {article.status === 'pending' && (
                      <Badge className="bg-[#FFCC33]/20 text-[#8B6914]">
                        <ClockIcon className="w-3 h-3 mr-1" />
                        На модерации
                      </Badge>
                    )}
                    {article.isProtected && (
                      <Badge variant="secondary" className="bg-[#3366CC]/10 text-[#3366CC]">
                        <Shield className="w-3 h-3 mr-1" />
                        Защищено
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-sm text-[#54595D] dark:text-[#aaa]">
                  <span className="flex items-center gap-1" title="Автор">
                    <User className="w-4 h-4" />
                    {article.author}
                  </span>
                  <span className="flex items-center gap-1" title="Категория">
                    <Folder className="w-4 h-4" />
                    {article.category}
                  </span>
                  <span className="flex items-center gap-1" title="Дата создания">
                    <Clock className="w-4 h-4" />
                    Создано: {formatDate(article.createdAt)}
                  </span>
                  {lastEdit && (
                    <span className="flex items-center gap-1" title="Последнее изменение">
                      <History className="w-4 h-4" />
                      Изменено: {formatDate(lastEdit.timestamp)} ({lastEdit.username})
                    </span>
                  )}
                </div>
              </div>

              {/* Article Body */}
              <div className="p-6">
                <div 
                  className="prose prose-lg max-w-none dark:prose-invert prose-headings:font-serif prose-headings:text-[#202122] dark:prose-headings:text-white prose-p:text-[#202122] dark:prose-p:text-[#ddd] prose-a:text-[#3366CC] prose-a:no-underline hover:prose-a:underline prose-code:bg-[#F8F9FA] dark:prose-code:bg-[#1a1a1a] prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-[#F8F9FA] dark:prose-pre:bg-[#1a1a1a] prose-pre:p-4 prose-pre:rounded-md prose-blockquote:border-l-[#3366CC] prose-table:w-full prose-table:border-collapse prose-th:border prose-th:border-[#C8CCD1] dark:prose-th:border-[#444] prose-th:p-2 prose-th:bg-[#F8F9FA] dark:prose-th:bg-[#1a1a1a] prose-td:border prose-td:border-[#C8CCD1] dark:prose-td:border-[#444] prose-td:p-2 prose-img:max-w-full prose-img:h-auto"
                  dangerouslySetInnerHTML={{ __html: parsedContent }}
                />
              </div>

              {/* Article Footer */}
              <div className="p-4 bg-[#F8F9FA] dark:bg-[#1a1a1a] border-t border-[#C8CCD1] dark:border-[#444]">
                <div className="flex flex-wrap items-center justify-between gap-4 text-sm text-[#54595D] dark:text-[#aaa]">
                  <div className="flex items-center gap-4">
                    <span>Автор: <strong className="text-[#202122] dark:text-white">{article.author}</strong></span>
                    <span>•</span>
                    <span>Создано: {formatDate(article.createdAt)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <History className="w-4 h-4" />
                    <span>{article.changelog.length} {article.changelog.length === 1 ? 'изменение' : article.changelog.length < 5 ? 'изменения' : 'изменений'}</span>
                  </div>
                </div>
              </div>
            </article>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions */}
            {canEdit() && (
              <div className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md p-4">
                <h3 className="font-semibold text-[#202122] dark:text-white mb-3">Действия</h3>
                <div className="space-y-2">
                  <Button
                    onClick={() => navigate(`/edit/${article.id}`)}
                    className="w-full bg-[#3366CC] hover:bg-[#2A56B0]"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Редактировать
                  </Button>

                  {(isAdmin || article.authorId === user?.id) && (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full border-[#DD3333] text-[#DD3333] hover:bg-[#DD3333] hover:text-white"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Удалить
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Удалить статью?</AlertDialogTitle>
                          <AlertDialogDescription>
                            Это действие нельзя отменить. Статья «{article.title}» будет удалена навсегда.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Отмена</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="bg-[#DD3333] hover:bg-[#BB2222]"
                          >
                            {isDeleting ? 'Удаление...' : 'Удалить'}
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  )}
                </div>
              </div>
            )}

            {/* Table of Contents */}
            <TOC headings={headings} />

            {/* Changelog */}
            <Changelog entries={article.changelog} maxEntries={3} />

            {/* Info */}
            <div className="bg-[#F8F9FA] dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md p-4">
              <h3 className="font-semibold text-[#202122] dark:text-white mb-2">Информация</h3>
              <p className="text-sm text-[#54595D] dark:text-[#aaa]">
                {isAdmin 
                  ? 'Вы можете редактировать любую статью как администратор.' 
                  : user 
                    ? 'Вы можете редактировать свои статьи.'
                    : 'Войдите, чтобы создавать и редактировать статьи.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
