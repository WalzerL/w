import { useState } from 'react';
import { History, ChevronDown, ChevronUp, User, Clock, Edit, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { ChangelogEntry } from '@/types';

interface ChangelogProps {
  entries: ChangelogEntry[];
  maxEntries?: number;
}

export function Changelog({ entries, maxEntries = 5 }: ChangelogProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getChangeIcon = (type: ChangelogEntry['type']) => {
    switch (type) {
      case 'create':
        return <Plus className="w-4 h-4 text-[#00AF89]" />;
      case 'edit':
        return <Edit className="w-4 h-4 text-[#3366CC]" />;
      case 'delete':
        return <Trash2 className="w-4 h-4 text-[#DD3333]" />;
      default:
        return <Edit className="w-4 h-4 text-[#72777D]" />;
    }
  };

  const getChangeBadge = (type: ChangelogEntry['type']) => {
    switch (type) {
      case 'create':
        return (
          <Badge className="bg-[#00AF89]/10 text-[#00AF89] hover:bg-[#00AF89]/20">
            Создание
          </Badge>
        );
      case 'edit':
        return (
          <Badge className="bg-[#3366CC]/10 text-[#3366CC] hover:bg-[#3366CC]/20">
            Редактирование
          </Badge>
        );
      case 'delete':
        return (
          <Badge className="bg-[#DD3333]/10 text-[#DD3333] hover:bg-[#DD3333]/20">
            Удаление
          </Badge>
        );
      default:
        return (
          <Badge variant="secondary">
            Изменение
          </Badge>
        );
    }
  };

  const displayedEntries = isExpanded ? entries : entries.slice(0, maxEntries);
  const hasMore = entries.length > maxEntries;

  if (entries.length === 0) {
    return (
      <div className="bg-[#F8F9FA] border border-[#C8CCD1] rounded-md p-4">
        <h3 className="flex items-center gap-2 font-semibold text-[#202122] mb-2">
          <History className="w-4 h-4" />
          История изменений
        </h3>
        <p className="text-sm text-[#54595D]">Нет записей об изменениях</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-[#C8CCD1] rounded-md overflow-hidden">
      <div className="p-4 border-b border-[#C8CCD1] bg-[#F8F9FA]">
        <h3 className="flex items-center gap-2 font-semibold text-[#202122]">
          <History className="w-4 h-4" />
          История изменений
          <span className="text-sm font-normal text-[#72777D]">
            ({entries.length})
          </span>
        </h3>
      </div>

      <div className="divide-y divide-[#C8CCD1]">
        {displayedEntries.map((entry) => (
          <div key={entry.id} className="p-4 hover:bg-[#F8F9FA] transition-colors">
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {getChangeIcon(entry.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  {getChangeBadge(entry.type)}
                  <span className="flex items-center gap-1 text-sm text-[#54595D]">
                    <User className="w-3 h-3" />
                    {entry.username}
                  </span>
                  <span className="flex items-center gap-1 text-sm text-[#72777D]">
                    <Clock className="w-3 h-3" />
                    {formatDate(entry.timestamp)}
                  </span>
                </div>
                
                <ul className="space-y-1 mt-2">
                  {entry.changes.map((change, idx) => (
                    <li 
                      key={idx}
                      className="text-sm text-[#202122] flex items-start gap-2"
                    >
                      <span className="text-[#3366CC] mt-1">•</span>
                      <span>{change}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>

      {hasMore && (
        <div className="p-3 border-t border-[#C8CCD1] bg-[#F8F9FA]">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full text-[#3366CC]"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4 mr-2" />
                Скрыть ({entries.length - maxEntries})
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-2" />
                Показать все ({entries.length})
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
