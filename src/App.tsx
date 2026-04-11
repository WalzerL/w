import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Home } from '@/pages/Home';
import { ArticlePage } from '@/pages/Article';
import { EditorPage } from '@/pages/Editor';
import { AdminPage } from '@/pages/Admin';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { useAuth } from '@/hooks/useAuth';
import { initializeStorage, getSettings } from '@/utils/storage';
import { Toaster } from '@/components/ui/sonner';

function App() {
  const { user, isAdmin, login, register, logout, isLoading } = useAuth();
  const [siteName, setSiteName] = useState('WalzerWiki');

  useEffect(() => {
    // Initialize localStorage with default data
    void initializeStorage();
    
    // Load site settings
    const settings = getSettings();
    setSiteName(settings.siteName);
    
    // Apply dark mode
    if (settings.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    // Update title
    document.title = settings.siteName;
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 bg-[#3366CC]/20 rounded-full mb-4" />
          <div className="w-32 h-4 bg-[#C8CCD1]/50 rounded" />
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#F8F9FA] dark:bg-[#1a1a1a]">
        <Header
          user={user}
          isAdmin={isAdmin}
          onLogin={login}
          onRegister={register}
          onLogout={logout}
          siteName={siteName}
        />
        
        <main>
          <Routes>
            <Route path="/" element={<Home user={user} isAdmin={isAdmin} />} />
            <Route path="/article/:id" element={<ArticlePage user={user} isAdmin={isAdmin} />} />
            <Route 
              path="/edit/:id?" 
              element={
                <ProtectedRoute isAllowed={!!user}>
                  <EditorPage user={user} isAdmin={isAdmin} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute isAllowed={isAdmin}>
                  <AdminPage isAdmin={isAdmin} />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>

        <Toaster />
      </div>
    </BrowserRouter>
  );
}

export default App;
