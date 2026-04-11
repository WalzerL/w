import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  FileText, 
  Settings, 
  Shield, 
  Plus, 
  Trash2, 
  Edit, 
  AlertCircle,
  Check,
  Save,
  User,
  Lock,
  Mail,
  Clock,
  CheckCircle,
  XCircle,
  Sun,
  Moon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useAuth } from '@/hooks/useAuth';
import { useArticles } from '@/hooks/useArticles';
import { getSettings, saveSettings, getPendingArticles, saveArticle } from '@/utils/storage';
import type { SiteSettings, User as UserType, Article } from '@/types';

interface AdminPageProps {
  isAdmin: boolean;
}

export function AdminPage({ isAdmin }: AdminPageProps) {
  const navigate = useNavigate();
  const { getAllUsers, createUser, updateUser, removeUser } = useAuth();
  const { getAll, remove } = useArticles();

  const [users, setUsers] = useState<UserType[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [pendingArticles, setPendingArticles] = useState<Article[]>([]);
  const [settings, setSettings] = useState<SiteSettings>(getSettings());
  
  // New user form
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserIsAdmin, setNewUserIsAdmin] = useState(false);
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = () => {
    setUsers(getAllUsers());
    setArticles(getAll());
    setPendingArticles(getPendingArticles());
  };

  const showMessage = (msg: string, isError = false) => {
    if (isError) {
      setError(msg);
      setSuccess('');
    } else {
      setSuccess(msg);
      setError('');
    }
    setTimeout(() => {
      setError('');
      setSuccess('');
    }, 3000);
  };

  const handleCreateUser = async () => {
    if (!newUserName.trim() || !newUserPassword.trim()) {
      showMessage('Введите имя пользователя и пароль', true);
      return;
    }

    if (newUserPassword.length < 10) {
      showMessage('Пароль должен быть не менее 10 символов', true);
      return;
    }

    const result = await createUser(
      newUserName.trim(), 
      newUserPassword.trim(), 
      newUserIsAdmin,
      newUserEmail.trim() || undefined
    );
    
    if (result.user) {
      setNewUserName('');
      setNewUserEmail('');
      setNewUserPassword('');
      setNewUserIsAdmin(false);
      refreshData();
      showMessage('Пользователь создан успешно');
    } else {
      showMessage(result.error || 'Ошибка при создании пользователя', true);
    }
  };

  const handleToggleAdmin = async (userId: string, currentStatus: boolean) => {
    const result = await updateUser(userId, { isAdmin: !currentStatus });
    if (result) {
      refreshData();
      showMessage('Права обновлены');
    } else {
      showMessage('Нельзя снять права с последнего администратора', true);
    }
  };

  const handleDeleteUser = (userId: string) => {
    const result = removeUser(userId);
    if (result.success) {
      refreshData();
      showMessage('Пользователь удален');
    } else {
      showMessage(result.error || 'Ошибка при удалении', true);
    }
  };

  const handleDeleteArticle = (articleId: string) => {
    const adminUser = users.find(u => u.isAdmin);
    if (adminUser) {
      remove(articleId, adminUser);
      refreshData();
      showMessage('Статья удалена');
    }
  };

  const handleApproveArticle = (article: Article) => {
    article.status = 'approved';
    saveArticle(article);
    refreshData();
    showMessage('Статья одобрена');
  };

  const handleRejectArticle = (article: Article) => {
    article.status = 'rejected';
    saveArticle(article);
    refreshData();
    showMessage('Статья отклонена');
  };

  const handleSaveSettings = () => {
    saveSettings(settings);
    showMessage('Настройки сохранены');
    // Apply dark mode
    if (settings.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const toggleDarkMode = () => {
    const newDarkMode = !settings.darkMode;
    setSettings({ ...settings, darkMode: newDarkMode });
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
        <div className="max-w-[960px] mx-auto px-4">
          <Alert variant="destructive" className="bg-[#DD3333]/10 border-[#DD3333]/30">
            <AlertCircle className="w-4 h-4" />
            <AlertDescription>
              Доступ запрещен. Только администраторы могут просматривать эту страницу.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] py-8">
      <div className="max-w-[960px] mx-auto px-4">
        <div className="flex items-center gap-4 mb-6">
          <Shield className="w-8 h-8 text-[#3366CC]" />
          <h1 className="text-2xl font-bold text-[#202122] dark:text-white font-serif">
            Панель администратора
          </h1>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-4 bg-[#DD3333]/10 border-[#DD3333]/30">
            <AlertCircle className="w-4 h-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4 bg-[#00AF89]/10 border-[#00AF89]/30 text-[#00AF89]">
            <Check className="w-4 h-4" />
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="moderation" className="space-y-6">
          <TabsList className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444]">
            <TabsTrigger value="moderation" className="data-[state=active]:bg-[#3366CC] data-[state=active]:text-white">
              <Clock className="w-4 h-4 mr-2" />
              Модерация
              {pendingArticles.length > 0 && (
                <Badge className="ml-2 bg-[#FFCC33] text-[#8B6914]">{pendingArticles.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-[#3366CC] data-[state=active]:text-white">
              <Users className="w-4 h-4 mr-2" />
              Пользователи
            </TabsTrigger>
            <TabsTrigger value="articles" className="data-[state=active]:bg-[#3366CC] data-[state=active]:text-white">
              <FileText className="w-4 h-4 mr-2" />
              Статьи
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-[#3366CC] data-[state=active]:text-white">
              <Settings className="w-4 h-4 mr-2" />
              Настройки
            </TabsTrigger>
          </TabsList>

          {/* Moderation Tab */}
          <TabsContent value="moderation" className="space-y-6">
            <div className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md p-4">
              <h3 className="font-semibold text-[#202122] dark:text-white mb-2 flex items-center gap-2">
                <Clock className="w-5 h-5 text-[#FFCC33]" />
                Статьи на модерации
              </h3>
              <p className="text-sm text-[#54595D] mb-4">
                Статьи, созданные обычными пользователями, ожидают вашего одобрения.
              </p>
            </div>

            {pendingArticles.length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md">
                <CheckCircle className="w-12 h-12 text-[#00AF89] mx-auto mb-4" />
                <p className="text-[#54595D]">Нет статей на модерации</p>
              </div>
            ) : (
              <div className="space-y-4">
                {pendingArticles.map((article) => (
                  <div key={article.id} className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-semibold text-[#202122] dark:text-white text-lg">{article.title}</h4>
                        <div className="flex items-center gap-4 mt-2 text-sm text-[#54595D]">
                          <span className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            {article.author}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {formatDate(article.createdAt)}
                          </span>
                          <Badge variant="secondary">{article.category}</Badge>
                        </div>
                        <p className="mt-3 text-sm text-[#54595D] line-clamp-3">
                          {article.content.slice(0, 200)}...
                        </p>
                      </div>
                      <div className="flex flex-col gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleApproveArticle(article)}
                          className="bg-[#00AF89] hover:bg-[#00997a]"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Одобрить
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/article/${article.id}`)}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          Просмотр
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRejectArticle(article)}
                          className="border-[#DD3333] text-[#DD3333] hover:bg-[#DD3333] hover:text-white"
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          Отклонить
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            {/* Create User */}
            <div className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md p-4">
              <h3 className="font-semibold text-[#202122] dark:text-white mb-4">Создать пользователя</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="new-username">Имя пользователя *</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                    <Input
                      id="new-username"
                      value={newUserName}
                      onChange={(e) => setNewUserName(e.target.value)}
                      placeholder="Имя"
                      className="pl-10"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="new-email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                    <Input
                      id="new-email"
                      type="email"
                      value={newUserEmail}
                      onChange={(e) => setNewUserEmail(e.target.value)}
                      placeholder="email@example.com"
                      className="pl-10"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="new-password">Пароль *</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                    <Input
                      id="new-password"
                      type="password"
                      value={newUserPassword}
                      onChange={(e) => setNewUserPassword(e.target.value)}
                      placeholder="Мин. 6 символов"
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="flex items-end gap-4">
                  <div className="flex items-center space-x-2 pb-2">
                    <Switch
                      id="new-is-admin"
                      checked={newUserIsAdmin}
                      onCheckedChange={setNewUserIsAdmin}
                    />
                    <Label htmlFor="new-is-admin">Админ</Label>
                  </div>
                  <Button onClick={handleCreateUser} className="bg-[#3366CC] hover:bg-[#2A56B0]">
                    <Plus className="w-4 h-4 mr-2" />
                    Создать
                  </Button>
                </div>
              </div>
            </div>

            {/* Users List */}
            <div className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Пользователь</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Создан</TableHead>
                    <TableHead className="text-right">Действия</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((u) => (
                    <TableRow key={u.id}>
                      <TableCell className="font-medium">{u.username}</TableCell>
                      <TableCell className="text-[#54595D]">{u.email || '—'}</TableCell>
                      <TableCell>
                        {u.isAdmin ? (
                          <Badge className="bg-[#3366CC]/10 text-[#3366CC] hover:bg-[#3366CC]/20">
                            <Shield className="w-3 h-3 mr-1" />
                            Администратор
                          </Badge>
                        ) : (
                          <Badge variant="secondary">Пользователь</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-[#54595D]">{formatDate(u.createdAt)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleAdmin(u.id, u.isAdmin)}
                          >
                            {u.isAdmin ? 'Снять права' : 'Сделать админом'}
                          </Button>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-[#DD3333] hover:text-[#DD3333]"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Удалить пользователя?</DialogTitle>
                                <DialogDescription>
                                  Пользователь {u.username} будет удален навсегда.
                                </DialogDescription>
                              </DialogHeader>
                              <DialogFooter>
                                <Button variant="outline">Отмена</Button>
                                <Button 
                                  variant="destructive"
                                  onClick={() => handleDeleteUser(u.id)}
                                >
                                  Удалить
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          {/* Articles Tab */}
          <TabsContent value="articles">
            <div className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Заголовок</TableHead>
                    <TableHead>Автор</TableHead>
                    <TableHead>Категория</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Обновлено</TableHead>
                    <TableHead className="text-right">Действия</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {articles.map((article) => (
                    <TableRow key={article.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {article.isProtected && <Shield className="w-4 h-4 text-[#FFCC33]" />}
                          {article.title}
                        </div>
                      </TableCell>
                      <TableCell>{article.author}</TableCell>
                      <TableCell>{article.category}</TableCell>
                      <TableCell>
                        {article.status === 'approved' && (
                          <Badge className="bg-[#00AF89]/10 text-[#00AF89]">Одобрена</Badge>
                        )}
                        {article.status === 'pending' && (
                          <Badge className="bg-[#FFCC33]/10 text-[#8B6914]">На модерации</Badge>
                        )}
                        {article.status === 'rejected' && (
                          <Badge className="bg-[#DD3333]/10 text-[#DD3333]">Отклонена</Badge>
                        )}
                      </TableCell>
                      <TableCell>{formatDate(article.updatedAt)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate(`/edit/${article.id}`)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-[#DD3333] hover:text-[#DD3333]"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Удалить статью?</DialogTitle>
                                <DialogDescription>
                                  Статья «{article.title}» будет удалена навсегда.
                                </DialogDescription>
                              </DialogHeader>
                              <DialogFooter>
                                <Button variant="outline">Отмена</Button>
                                <Button 
                                  variant="destructive"
                                  onClick={() => handleDeleteArticle(article.id)}
                                >
                                  Удалить
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <div className="bg-white dark:bg-[#2a2a2a] border border-[#C8CCD1] dark:border-[#444] rounded-md p-6 space-y-6">
              <div>
                <Label htmlFor="site-name">Название сайта</Label>
                <Input
                  id="site-name"
                  value={settings.siteName}
                  onChange={(e) => setSettings({ ...settings, siteName: e.target.value })}
                  placeholder="WalzerWiki"
                />
              </div>
              <div>
                <Label htmlFor="site-description">Описание сайта</Label>
                <Input
                  id="site-description"
                  value={settings.siteDescription}
                  onChange={(e) => setSettings({ ...settings, siteDescription: e.target.value })}
                  placeholder="База знаний сообщества"
                />
              </div>
              
              {/* Dark Mode Toggle */}
              <div className="flex items-center justify-between p-4 bg-[#F8F9FA] dark:bg-[#1a1a1a] rounded-md">
                <div>
                  <Label className="font-medium flex items-center gap-2">
                    {settings.darkMode ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                    Темная тема
                  </Label>
                  <p className="text-sm text-[#54595D]">
                    Переключить между светлой и темной темой
                  </p>
                </div>
                <Switch
                  checked={settings.darkMode}
                  onCheckedChange={toggleDarkMode}
                />
              </div>

              <div className="flex items-center justify-between p-4 bg-[#F8F9FA] dark:bg-[#1a1a1a] rounded-md">
                <div>
                  <Label htmlFor="allow-registration" className="font-medium">
                    Разрешить регистрацию
                  </Label>
                  <p className="text-sm text-[#54595D]">
                    Новые пользователи смогут регистрироваться самостоятельно
                  </p>
                </div>
                <Switch
                  id="allow-registration"
                  checked={settings.allowRegistration}
                  onCheckedChange={(checked) => 
                    setSettings({ ...settings, allowRegistration: checked })
                  }
                />
              </div>
              <Button onClick={handleSaveSettings} className="bg-[#3366CC] hover:bg-[#2A56B0]">
                <Save className="w-4 h-4 mr-2" />
                Сохранить настройки
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Need to import Eye for the moderation tab
import { Eye } from 'lucide-react';
