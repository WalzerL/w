import { useNavigate } from 'react-router-dom';
import { FileText, Clock, Folder, User, Shield } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Article } from '@/types';

interface ArticleCardProps {
  article: Article;
}

export function ArticleCard({ article }: ArticleCardProps) {
  const navigate = useNavigate();

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  // Get last editor info
  const lastEdit = article.changelog[article.changelog.length - 1];

  return (
    <Card 
      onClick={() => navigate(`/article/${article.id}`)}
      className="cursor-pointer border-[#C8CCD1] hover:border-[#3366CC] hover:shadow-md transition-all duration-200 group"
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-[#F8F9FA] rounded-lg group-hover:bg-[#3366CC]/10 transition-colors">
            <FileText className="w-5 h-5 text-[#72777D] group-hover:text-[#3366CC] transition-colors" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-[#202122] group-hover:text-[#3366CC] transition-colors line-clamp-1">
                {article.title}
              </h3>
              {article.isProtected && (
                <Badge variant="secondary" className="bg-[#FFCC33]/20 text-[#8B6914] flex-shrink-0">
                  <Shield className="w-3 h-3 mr-1" />
                </Badge>
              )}
            </div>
            <p className="text-sm text-[#54595D] mt-1 line-clamp-2">
              {article.content.slice(0, 150)}...
            </p>
            <div className="flex items-center gap-4 mt-3 text-xs text-[#72777D] flex-wrap">
              <span className="flex items-center gap-1">
                <User className="w-3 h-3" />
                {article.author}
              </span>
              <span className="flex items-center gap-1">
                <Folder className="w-3 h-3" />
                {article.category}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDate(article.updatedAt)}
              </span>
              {lastEdit && lastEdit.username !== article.author && (
                <span className="text-[#3366CC]">
                  (ред. {lastEdit.username})
                </span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
