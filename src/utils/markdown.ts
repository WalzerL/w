// Simple Markdown parser

export function parseMarkdown(markdown: string): string {
  if (!markdown) return '';

  let html = markdown;

  // Escape HTML
  html = html.replace(/&/g, '&amp;')
             .replace(/</g, '&lt;')
             .replace(/>/g, '&gt;');

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.*?)_/g, '<em>$1</em>');

  // Strikethrough
  html = html.replace(/~~(.*?)~~/g, '<del>$1</del>');

  // Code inline
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Code block
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Images
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="max-w-full h-auto" />');

  // Blockquote
  html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

  // Unordered list
  html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // Ordered list
  html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
  
  // Tables (simple)
  const tableRegex = /\|(.+)\|\n\|[-:\|\s]+\|\n((?:\|.+\|\n?)+)/g;
  html = html.replace(tableRegex, (_match, header, rows) => {
    const headers = header.split('|').map((h: string) => h.trim()).filter(Boolean);
    const headerHtml = headers.map((h: string) => `<th>${h}</th>`).join('');
    
    const rowLines = rows.trim().split('\n');
    const rowsHtml = rowLines.map((line: string) => {
      const cells = line.split('|').map((c: string) => c.trim()).filter(Boolean);
      return `<tr>${cells.map((c: string) => `<td>${c}</td>`).join('')}</tr>`;
    }).join('');
    
    return `<table class="w-full border-collapse border border-[#C8CCD1] my-4"><thead><tr>${headerHtml}</tr></thead><tbody>${rowsHtml}</tbody></table>`;
  });

  // Horizontal rule
  html = html.replace(/^---$/gim, '<hr class="my-4 border-[#C8CCD1]" />');

  // Line breaks
  html = html.replace(/\n/g, '<br />');

  // Wrap in paragraphs (simple approach)
  const lines = html.split('<br />');
  let result = '';
  let inList = false;
  let listContent = '';

  for (const line of lines) {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('<li>')) {
      if (!inList) {
        inList = true;
        listContent = '';
      }
      listContent += trimmed;
    } else if (inList && !trimmed.startsWith('<li>')) {
      result += `<ul class="list-disc pl-6 my-2">${listContent}</ul>`;
      inList = false;
      if (trimmed && !trimmed.startsWith('<')) {
        result += `<p>${trimmed}</p>`;
      } else {
        result += trimmed;
      }
    } else if (trimmed && !trimmed.startsWith('<')) {
      result += `<p class="my-2">${trimmed}</p>`;
    } else {
      result += trimmed;
    }
  }

  if (inList) {
    result += `<ul class="list-disc pl-6 my-2">${listContent}</ul>`;
  }

  return result;
}

// Extract headings for TOC
export interface Heading {
  level: number;
  text: string;
  id: string;
}

export function extractHeadings(markdown: string): Heading[] {
  const headings: Heading[] = [];
  const lines = markdown.split('\n');

  for (const line of lines) {
    const match = line.match(/^(#{1,3})\s+(.+)$/);
    if (match) {
      const level = match[1].length;
      const text = match[2].trim();
      const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
      headings.push({ level, text, id });
    }
  }

  return headings;
}
