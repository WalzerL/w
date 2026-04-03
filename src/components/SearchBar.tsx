import { useState, useEffect, useRef } from 'react';
import { Search, X, FileText } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useArticles } from '@/hooks/useArticles';
import type { Article } from '@/types';

interface SearchBarProps {
  onSelect?: (article: Article) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

export function SearchBar({ onSelect, placeholder = 'Поиск статей...', autoFocus = false }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Article[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const { search } = useArticles();
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim()) {
      const searchResults = search(query);
      setResults(searchResults.slice(0, 5));
      setIsOpen(true);
    } else {
      setResults([]);
      setIsOpen(false);
    }
  }, [query, search]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (article: Article) => {
    setQuery('');
    setIsOpen(false);
    onSelect?.(article);
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-xl">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#72777D]" />
        <Input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className="pl-10 pr-10 py-2.5 w-full border-[#C8CCD1] focus:border-[#3366CC] focus:ring-2 focus:ring-[#3366CC]/20 transition-all"
        />
        {query && (
          <Button
            variant="ghost"
            size="icon"
            onClick={clearSearch}
            className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-[#72777D] hover:text-[#202122]"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-[#C8CCD1] rounded-md shadow-lg z-50 overflow-hidden">
          {results.map((article) => (
            <button
              key={article.id}
              onClick={() => handleSelect(article)}
              className="w-full px-4 py-3 flex items-start gap-3 hover:bg-[#F8F9FA] text-left border-b border-[#C8CCD1] last:border-b-0 transition-colors"
            >
              <FileText className="w-5 h-5 text-[#72777D] mt-0.5 flex-shrink-0" />
              <div className="min-w-0">
                <p className="font-medium text-[#202122] truncate">{article.title}</p>
                <p className="text-sm text-[#54595D] line-clamp-1">
                  {article.content.slice(0, 100)}...
                </p>
                <span className="inline-block mt-1 text-xs text-[#3366CC] bg-[#3366CC]/10 px-2 py-0.5 rounded">
                  {article.category}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {isOpen && query && results.length === 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-[#C8CCD1] rounded-md shadow-lg z-50 p-4 text-center text-[#54595D]">
          Статьи не найдены
        </div>
      )}
    </div>
  );
}
