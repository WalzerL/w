import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  isAllowed: boolean;
  children: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({ 
  isAllowed, 
  children, 
  redirectTo = '/' 
}: ProtectedRouteProps) {
  if (!isAllowed) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
