import { List } from 'lucide-react';
import type { Heading } from '@/utils/markdown';

interface TOCProps {
  headings: Heading[];
}

export function TOC({ headings }: TOCProps) {
  if (headings.length === 0) return null;

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="bg-[#F8F9FA] border border-[#C8CCD1] rounded-md p-4">
      <h3 className="flex items-center gap-2 font-semibold text-[#202122] mb-3">
        <List className="w-4 h-4" />
        Содержание
      </h3>
      <nav>
        <ul className="space-y-1">
          {headings.map((heading, index) => (
            <li 
              key={index}
              className={`
                ${heading.level === 1 ? 'font-medium' : ''}
                ${heading.level === 2 ? 'pl-3' : ''}
                ${heading.level === 3 ? 'pl-6 text-sm' : ''}
              `}
            >
              <a
                href={`#${heading.id}`}
                onClick={(e) => handleClick(e, heading.id)}
                className="text-[#3366CC] hover:underline block py-0.5"
              >
                {heading.text}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
