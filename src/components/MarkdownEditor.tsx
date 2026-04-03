import { useState, useRef } from 'react';
import { Eye, Edit, HelpCircle, Image, Link, Bold, Italic, List, ListOrdered, Quote, Code } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { FileUploader } from './FileUploader';
import { parseMarkdown } from '@/utils/markdown';
import type { User, UploadedFile } from '@/types';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  user: User;
}

const MARKDOWN_HELP = `
# Заголовок 1
## Заголовок 2
### Заголовок 3

**Жирный текст**
*Курсив*
~~Зачеркнутый~~

- Список пункт 1
- Список пункт 2
  - Вложенный пункт

1. Нумерованный список
2. Второй пункт

[Ссылка](https://example.com)

![Изображение](data:image/...)

\`код в строке\`

\`\`\`
блок кода
\`\`\`

> Цитата

| Таблица | Колонка 2 |
|---------|-----------|
| Данные  | Данные 2  |
`;

export function MarkdownEditor({ value, onChange, placeholder, user }: MarkdownEditorProps) {
  const [activeTab, setActiveTab] = useState('edit');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const insertText = (before: string, after: string = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    const newText = value.substring(0, start) + before + selectedText + after + value.substring(end);
    
    onChange(newText);
    
    // Restore focus and selection
    setTimeout(() => {
      textarea.focus();
      const newCursorPos = start + before.length + selectedText.length;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  const insertImage = (file: UploadedFile) => {
    const imageMarkdown = `![${file.name}](${file.data})`;
    insertText('\n' + imageMarkdown + '\n');
  };

  const toolbarButtons = [
    { icon: Bold, action: () => insertText('**', '**'), title: 'Жирный' },
    { icon: Italic, action: () => insertText('*', '*'), title: 'Курсив' },
    { icon: List, action: () => insertText('- '), title: 'Список' },
    { icon: ListOrdered, action: () => insertText('1. '), title: 'Нумерованный список' },
    { icon: Quote, action: () => insertText('> '), title: 'Цитата' },
    { icon: Code, action: () => insertText('```\n', '\n```'), title: 'Код' },
    { icon: Link, action: () => insertText('[', '](url)'), title: 'Ссылка' },
  ];

  return (
    <div className="border border-[#C8CCD1] rounded-md overflow-hidden">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="flex items-center justify-between px-3 py-2 bg-[#F8F9FA] border-b border-[#C8CCD1]">
          <div className="flex items-center gap-2">
            <TabsList className="bg-transparent p-0 h-auto gap-1">
              <TabsTrigger 
                value="edit" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-3 py-1.5 text-sm"
              >
                <Edit className="w-4 h-4 mr-2" />
                Редактировать
              </TabsTrigger>
              <TabsTrigger 
                value="preview"
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm px-3 py-1.5 text-sm"
              >
                <Eye className="w-4 h-4 mr-2" />
                Предпросмотр
              </TabsTrigger>
            </TabsList>

            {/* Toolbar */}
            {activeTab === 'edit' && (
              <div className="hidden sm:flex items-center gap-1 ml-4 border-l border-[#C8CCD1] pl-4">
                {toolbarButtons.map((btn, idx) => (
                  <Button
                    key={idx}
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={btn.action}
                    title={btn.title}
                    className="h-8 w-8"
                  >
                    <btn.icon className="w-4 h-4" />
                  </Button>
                ))}
                
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      title="Вставить изображение"
                      className="h-8 w-8"
                    >
                      <Image className="w-4 h-4" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80">
                    <FileUploader 
                      user={user} 
                      insertIntoEditor={insertImage}
                    />
                  </PopoverContent>
                </Popover>
              </div>
            )}
          </div>

          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 text-[#72777D]">
                <HelpCircle className="w-4 h-4 mr-2" />
                Справка
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg max-h-[80vh] overflow-auto">
              <DialogHeader>
                <DialogTitle>Синтаксис Markdown</DialogTitle>
                <DialogDescription>
                  Используйте Markdown для форматирования текста статьи.
                </DialogDescription>
              </DialogHeader>
              <pre className="bg-[#F8F9FA] p-4 rounded-md text-sm overflow-auto">
                {MARKDOWN_HELP}
              </pre>
            </DialogContent>
          </Dialog>
        </div>

        <TabsContent value="edit" className="m-0">
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder || 'Введите содержание статьи...'}
            className="min-h-[400px] border-0 rounded-none resize-y focus-visible:ring-0 focus-visible:ring-offset-0 font-mono text-sm"
          />
        </TabsContent>

        <TabsContent value="preview" className="m-0">
          <div 
            className="min-h-[400px] p-4 prose prose-sm max-w-none prose-headings:font-serif prose-headings:text-[#202122] prose-p:text-[#202122] prose-a:text-[#3366CC] prose-a:no-underline hover:prose-a:underline prose-code:bg-[#F8F9FA] prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-[#F8F9FA] prose-pre:p-4 prose-pre:rounded-md prose-blockquote:border-l-[#3366CC] prose-img:max-w-full prose-img:h-auto"
            dangerouslySetInnerHTML={{ __html: parseMarkdown(value) || '<p class="text-[#72777D] italic">Нет содержимого для предпросмотра...</p>' }}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
