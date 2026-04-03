import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, X, ArrowLeft, AlertCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { MarkdownEditor } from '@/components/MarkdownEditor';
import { useArticles } from '@/hooks/useArticles';
import type { User } from '@/types';

interface EditorPageProps {
  user: User | null;
  isAdmin: boolean;
}

export function EditorPage({ user, isAdmin }: EditorPageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getById, create, update, getCategories } = useArticles();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [isProtected, setIsProtected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<string[]>([]);

  const isEditing = !!id;

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }

    setCategories(getCategories());

    if (isEditing && id) {
      const article = getById(id);
      if (article) {
        // Check permissions
        if (!isAdmin && article.authorId !== user.id) {
          navigate(`/article/${id}`);
          return;
        }
        
        setTitle(article.title);
        setContent(article.content);
        setCategory(article.category);
        setIsProtected(article.isProtected);
      } else {
        navigate('/');
      }
    }
  }, [id, isEditing, getById, getCategories, navigate, user, isAdmin]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!user) {
      setError('Необходимо войти в систему');
      return;
    }

    // Validation
    if (!title.trim()) {
      setError('Введите заголовок статьи');
      return;
    }
    if (!content.trim()) {
      setError('Введите содержание статьи');
      return;
    }
    if (!category && !newCategory) {
      setError('Выберите или создайте категорию');
      return;
    }

    setIsLoading(true);

    try {
      const finalCategory = newCategory || category;

      if (isEditing && id) {
        const existingArticle = getById(id);
        if (!existingArticle) {
          setError('Статья не найдена');
          setIsLoading(false);
          return;
        }

        // Only admin can change protection
        const canChangeProtection = isAdmin;
        
        update(id, {
          title: title.trim(),
          content: content.trim(),
          category: finalCategory,
          isProtected: canChangeProtection ? isProtected : existingArticle.isProtected,
        }, user);
        
        navigate(`/article/${id}`);
      } else {
        // New article - set status based on user type
        const newArticle = create({
          title: title.trim(),
          content: content.trim(),
          category: finalCategory,
          author: user.username,
          isProtected: isAdmin ? isProtected : false,
          status: isAdmin ? 'approved' : 'pending', // Admin articles auto-approved
        }, user);
        
        if (isAdmin) {
          navigate(`/article/${newArticle.id}`);
        } else {
          // Show pending message for regular users
          navigate('/?pending=true');
        }
      }
    } catch {
      setError('Произошла ошибка при сохранении');
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (isEditing && id) {
      navigate(`/article/${id}`);
    } else {
      navigate('/');
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
        <div className="max-w-[960px] mx-auto px-4">
          <Alert variant="destructive" className="bg-[#DD3333]/10 border-[#DD3333]/30">
            <AlertCircle className="w-4 h-4" />
            <AlertDescription>
              Необходимо войти в систему для создания и редактирования статей.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
      <div className="max-w-[960px] mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              className="text-[#54595D]"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад
            </Button>
            <h1 className="text-2xl font-bold text-[#202122] dark:text-white font-serif">
              {isEditing ? 'Редактирование статьи' : 'Создание статьи'}
            </h1>
          </div>
        </div>

        {/* Moderation notice for non-admins creating new article */}
        {!isAdmin && !isEditing && (
          <Alert className="mb-6 bg-[#FFCC33]/10 border-[#FFCC33]/30">
            <Clock className="w-4 h-4 text-[#8B6914]" />
            <AlertDescription className="text-[#8B6914]">
              Ваша статья будет отправлена на модерацию. После одобрения администратором она появится на сайте.
            </AlertDescription>
          </Alert>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive" className="bg-[#DD3333]/10 border-[#DD3333]/30">
              <AlertCircle className="w-4 h-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Заголовок</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Введите заголовок статьи"
              className="text-lg"
            />
          </div>

          {/* Category */}
          <div className="space-y-2">
            <Label>Категория</Label>
            <div className="flex gap-2">
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Выберите категорию" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <span className="self-center text-[#54595D]">или</span>
              <Input
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="Новая категория"
                className="flex-1"
              />
            </div>
          </div>

          {/* Content */}
          <div className="space-y-2">
            <Label>Содержание</Label>
            <MarkdownEditor
              value={content}
              onChange={setContent}
              placeholder="Введите содержание статьи в формате Markdown..."
              user={user}
            />
          </div>

          {/* Protection - only for admins */}
          {isAdmin && (
            <div className="flex items-center justify-between p-4 bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md">
              <div>
                <Label htmlFor="protected" className="font-medium">
                  Защитить статью от вандализма
                </Label>
                <p className="text-sm text-[#54595D]">
                  Защищенные статьи могут редактировать только администраторы
                </p>
              </div>
              <Switch
                id="protected"
                checked={isProtected}
                onCheckedChange={setIsProtected}
              />
            </div>
          )}

          {/* Info for non-admins */}
          {!isAdmin && (
            <div className="p-4 bg-[#F8F9FA] dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md">
              <p className="text-sm text-[#54595D]">
                <strong>Примечание:</strong> Вы создаете статью от своего имени. 
                После сохранения статья будет отправлена на модерацию.
                {isEditing && ' Редактировать смогут только вы и администраторы.'}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-[#C8CCD1] dark:border-[#444]">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
            >
              <X className="w-4 h-4 mr-2" />
              Отмена
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-[#3366CC] hover:bg-[#2A56B0]"
            >
              <Save className="w-4 h-4 mr-2" />
              {isLoading ? 'Сохранение...' : (isAdmin ? 'Сохранить' : 'Отправить на модерацию')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
