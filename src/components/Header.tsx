import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, Menu, X, Shield, LogOut, User, Plus, Settings, Sun, Moon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { LoginDialog } from './LoginDialog';
import { getSettings, saveSettings } from '@/utils/storage';
import type { User as UserType } from '@/types';

interface HeaderProps {
  user: UserType | null;
  isAdmin: boolean;
  onLogin: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  onRegister: (username: string, password: string, email?: string) => Promise<{ success: boolean; error?: string }>;
  onLogout: () => void;
  siteName: string;
}

export function Header({ user, isAdmin, onLogin, onRegister, onLogout, siteName }: HeaderProps) {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const settings = getSettings();
    setDarkMode(settings.darkMode);
    if (settings.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    const settings = getSettings();
    saveSettings({ ...settings, darkMode: newDarkMode });
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-[#202122]/95 backdrop-blur border-b border-[#A2A9B1] dark:border-[#3A4048] shadow-sm">
      <div className="max-w-[1080px] mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <BookOpen className="w-6 h-6 text-[#3366CC] transition-transform group-hover:scale-110" />
            <span className="text-lg font-semibold text-[#202122] dark:text-white">
              {siteName}
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/')}
              className="text-[#54595D] dark:text-[#C8CCD1] hover:text-[#202122] dark:hover:text-[#F8F9FA] hover:bg-[#EAECF0] dark:hover:bg-[#2A2F36]"
            >
              Главная
            </Button>
            
            {user && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/edit')}
                className="text-[#54595D] dark:text-[#C8CCD1] hover:text-[#202122] dark:hover:text-[#F8F9FA] hover:bg-[#EAECF0] dark:hover:bg-[#2A2F36]"
              >
                <Plus className="w-4 h-4 mr-1" />
                Создать
              </Button>
            )}
            
            {isAdmin && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/admin')}
                className="text-[#54595D] dark:text-[#C8CCD1] hover:text-[#202122] dark:hover:text-[#F8F9FA] hover:bg-[#EAECF0] dark:hover:bg-[#2A2F36]"
              >
                <Settings className="w-4 h-4 mr-1" />
                Админ
              </Button>
            )}
          </nav>

          {/* User Actions */}
          <div className="flex items-center gap-2">
            {/* Dark Mode Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleDarkMode}
              className="text-[#54595D] dark:text-[#C8CCD1] hover:bg-[#EAECF0] dark:hover:bg-[#2A2F36]"
              title={darkMode ? 'Светлая тема' : 'Темная тема'}
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>

            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="text-[#54595D] dark:text-[#C8CCD1] hover:text-[#202122] dark:hover:text-[#F8F9FA] hover:bg-[#EAECF0] dark:hover:bg-[#2A2F36]"
                  >
                    <User className="w-4 h-4 mr-2" />
                    <span className="hidden sm:inline">{user.username}</span>
                    {isAdmin && (
                      <Shield className="w-3 h-3 ml-2 text-[#3366CC]" />
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem className="text-sm text-[#54595D] flex flex-col items-start">
                    <span className="font-medium text-[#202122]">{user.username}</span>
                    <span className="text-xs">{isAdmin ? 'Администратор' : 'Пользователь'}</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  {isAdmin && (
                    <DropdownMenuItem onClick={() => navigate('/admin')}>
                      <Settings className="w-4 h-4 mr-2" />
                      Панель администратора
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={onLogout} className="text-[#DD3333]">
                    <LogOut className="w-4 h-4 mr-2" />
                    Выйти
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsLoginOpen(true)}
                className="border-[#3366CC] text-[#3366CC] hover:bg-[#3366CC] hover:text-white"
              >
                <User className="w-4 h-4 mr-2" />
                Войти
              </Button>
            )}

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden text-[#54595D] dark:text-[#C8CCD1] hover:bg-[#EAECF0] dark:hover:bg-[#2A2F36]"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <nav className="md:hidden py-3 border-t border-[#A2A9B1] dark:border-[#3A4048] space-y-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                navigate('/');
                setIsMobileMenuOpen(false);
              }}
              className="w-full justify-start text-[#54595D] dark:text-[#C8CCD1]"
            >
              Главная
            </Button>
            {user && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  navigate('/edit');
                  setIsMobileMenuOpen(false);
                }}
                className="w-full justify-start text-[#54595D] dark:text-[#C8CCD1]"
              >
                <Plus className="w-4 h-4 mr-2" />
                Создать статью
              </Button>
            )}
            {isAdmin && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  navigate('/admin');
                  setIsMobileMenuOpen(false);
                }}
                className="w-full justify-start text-[#54595D] dark:text-[#C8CCD1]"
              >
                <Settings className="w-4 h-4 mr-2" />
                Панель администратора
              </Button>
            )}
          </nav>
        )}
      </div>

      <LoginDialog 
        isOpen={isLoginOpen} 
        onClose={() => setIsLoginOpen(false)} 
        onLogin={onLogin}
        onRegister={onRegister}
      />
    </header>
  );
}
