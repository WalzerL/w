import { useState } from 'react';
import { Shield, Eye, EyeOff, Lock, User, Mail, UserPlus, LogIn } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface LoginDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  onRegister: (username: string, password: string, email?: string) => Promise<{ success: boolean; error?: string }>;
}

export function LoginDialog({ isOpen, onClose, onLogin, onRegister }: LoginDialogProps) {
  const [activeTab, setActiveTab] = useState('login');
  
  // Login form state
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  
  // Register form state
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerPasswordConfirm, setRegisterPasswordConfirm] = useState('');
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const resetForms = () => {
    setLoginUsername('');
    setLoginPassword('');
    setRegisterUsername('');
    setRegisterEmail('');
    setRegisterPassword('');
    setRegisterPasswordConfirm('');
    setError('');
    setShowLoginPassword(false);
    setShowRegisterPassword(false);
  };

  const handleClose = () => {
    resetForms();
    onClose();
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!loginUsername.trim() || !loginPassword) {
      setError('Введите имя пользователя и пароль');
      setIsLoading(false);
      return;
    }

    try {
      const result = await onLogin(loginUsername.trim(), loginPassword);
      if (result.success) {
        resetForms();
        onClose();
      } else {
        setError(result.error || 'Ошибка входа');
      }
    } catch {
      setError('Произошла ошибка. Попробуйте позже.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Validation
    if (!registerUsername.trim() || !registerPassword) {
      setError('Заполните все обязательные поля');
      setIsLoading(false);
      return;
    }

    if (registerUsername.length < 3) {
      setError('Имя пользователя должно быть не менее 3 символов');
      setIsLoading(false);
      return;
    }

    if (registerPassword.length < 6) {
      setError('Пароль должен быть не менее 6 символов');
      setIsLoading(false);
      return;
    }

    if (registerPassword !== registerPasswordConfirm) {
      setError('Пароли не совпадают');
      setIsLoading(false);
      return;
    }

    try {
      const result = await onRegister(
        registerUsername.trim(), 
        registerPassword,
        registerEmail.trim() || undefined
      );
      if (result.success) {
        resetForms();
        onClose();
      } else {
        setError(result.error || 'Ошибка регистрации');
      }
    } catch {
      setError('Произошла ошибка. Попробуйте позже.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#3366CC]" />
            {activeTab === 'login' ? 'Вход в аккаунт' : 'Регистрация'}
          </DialogTitle>
          <DialogDescription>
            {activeTab === 'login' 
              ? 'Введите свои данные для входа в систему.' 
              : 'Создайте новый аккаунт для доступа к редактированию.'}
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">
              <LogIn className="w-4 h-4 mr-2" />
              Вход
            </TabsTrigger>
            <TabsTrigger value="register">
              <UserPlus className="w-4 h-4 mr-2" />
              Регистрация
            </TabsTrigger>
          </TabsList>

          {error && (
            <Alert variant="destructive" className="mt-4 bg-[#DD3333]/10 border-[#DD3333]/30 text-[#DD3333]">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <TabsContent value="login" className="mt-4">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-username">Имя пользователя</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                  <Input
                    id="login-username"
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                    placeholder="Введите имя пользователя"
                    className="pl-10"
                    autoFocus
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="login-password">Пароль</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                  <Input
                    id="login-password"
                    type={showLoginPassword ? 'text' : 'password'}
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Введите пароль"
                    className="pl-10 pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowLoginPassword(!showLoginPassword)}
                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-[#72777D]"
                  >
                    {showLoginPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  disabled={isLoading}
                >
                  Отмена
                </Button>
                <Button
                  type="submit"
                  disabled={!loginUsername || !loginPassword || isLoading}
                  className="bg-[#3366CC] hover:bg-[#2A56B0]"
                >
                  {isLoading ? 'Вход...' : 'Войти'}
                </Button>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="register" className="mt-4">
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="register-username">Имя пользователя *</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                  <Input
                    id="register-username"
                    value={registerUsername}
                    onChange={(e) => setRegisterUsername(e.target.value)}
                    placeholder="Придумайте имя (мин. 3 символа)"
                    className="pl-10"
                    autoFocus
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-email">Email (необязательно)</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                  <Input
                    id="register-email"
                    type="email"
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-password">Пароль *</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                  <Input
                    id="register-password"
                    type={showRegisterPassword ? 'text' : 'password'}
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    placeholder="Минимум 6 символов"
                    className="pl-10 pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowRegisterPassword(!showRegisterPassword)}
                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-[#72777D]"
                  >
                    {showRegisterPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-password-confirm">Подтвердите пароль *</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#72777D]" />
                  <Input
                    id="register-password-confirm"
                    type={showRegisterPassword ? 'text' : 'password'}
                    value={registerPasswordConfirm}
                    onChange={(e) => setRegisterPasswordConfirm(e.target.value)}
                    placeholder="Повторите пароль"
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="text-xs text-[#54595D] bg-[#F8F9FA] p-3 rounded-md">
                <p className="font-medium mb-1">Требования:</p>
                <ul className="list-disc list-inside space-y-0.5">
                  <li>Имя: минимум 3 символа</li>
                  <li>Пароль: минимум 6 символов</li>
                  <li>Пароли должны совпадать</li>
                </ul>
              </div>

              <div className="flex gap-2 justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  disabled={isLoading}
                >
                  Отмена
                </Button>
                <Button
                  type="submit"
                  disabled={!registerUsername || !registerPassword || !registerPasswordConfirm || isLoading}
                  className="bg-[#3366CC] hover:bg-[#2A56B0]"
                >
                  {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                </Button>
              </div>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
