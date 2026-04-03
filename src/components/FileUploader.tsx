import { useState, useRef, useCallback } from 'react';
import { Upload, Image, File } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useFiles } from '@/hooks/useFiles';
import type { User, UploadedFile } from '@/types';

interface FileUploaderProps {
  user: User;
  onFileSelect?: (file: UploadedFile) => void;
  insertIntoEditor?: (file: UploadedFile) => void;
}

export function FileUploader({ user, onFileSelect, insertIntoEditor }: FileUploaderProps) {
  const { uploadMultipleFiles, getImageFiles } = useFiles();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [showGallery, setShowGallery] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const results = await uploadMultipleFiles(files, user);
    
    const successful = results
      .filter(r => r.success && r.file)
      .map(r => r.file!);
    
    setUploadedFiles(prev => [...successful, ...prev]);
    
    // Notify parent about first uploaded file
    if (successful.length > 0 && onFileSelect) {
      onFileSelect(successful[0]);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const results = await uploadMultipleFiles(files, user);
      const successful = results
        .filter(r => r.success && r.file)
        .map(r => r.file!);
      setUploadedFiles(prev => [...successful, ...prev]);
    }
  }, [uploadMultipleFiles, user]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const openGallery = () => {
    setUploadedFiles(getImageFiles());
    setShowGallery(true);
  };

  const handleInsertImage = (file: UploadedFile) => {
    if (insertIntoEditor) {
      insertIntoEditor(file);
    }
    setShowGallery(false);
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-[#C8CCD1] rounded-lg p-6 text-center hover:border-[#3366CC] hover:bg-[#3366CC]/5 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.pdf,.txt,.md"
          onChange={handleFileSelect}
          className="hidden"
        />
        <Upload className="w-8 h-8 text-[#72777D] mx-auto mb-2" />
        <p className="text-sm text-[#54595D]">
          <span className="text-[#3366CC] font-medium">Нажмите</span> или перетащите файлы
        </p>
        <p className="text-xs text-[#72777D] mt-1">
          Изображения, PDF, текст (макс. 5MB)
        </p>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={openGallery}
          className="flex-1"
        >
          <Image className="w-4 h-4 mr-2" />
          Галерея
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          className="flex-1"
        >
          <File className="w-4 h-4 mr-2" />
          Файл
        </Button>
      </div>

      {/* Recently Uploaded */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-[#202122]">Загружено:</p>
          <div className="space-y-2">
            {uploadedFiles.slice(0, 3).map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-2 p-2 bg-[#F8F9FA] rounded-md"
              >
                {file.type.startsWith('image/') ? (
                  <img
                    src={file.data}
                    alt={file.name}
                    className="w-10 h-10 object-cover rounded"
                  />
                ) : (
                  <File className="w-10 h-10 text-[#72777D]" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{file.name}</p>
                  <p className="text-xs text-[#72777D]">
                    {new Date(file.uploadedAt).toLocaleDateString('ru-RU')}
                  </p>
                </div>
                {insertIntoEditor && file.type.startsWith('image/') && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleInsertImage(file)}
                  >
                    Вставить
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Gallery Dialog */}
      <Dialog open={showGallery} onOpenChange={setShowGallery}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
          <DialogHeader>
            <DialogTitle>Галерея изображений</DialogTitle>
            <DialogDescription>
              Выберите изображение для вставки в статью
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid grid-cols-3 gap-4 mt-4">
            {uploadedFiles.map((file) => (
              <button
                key={file.id}
                onClick={() => handleInsertImage(file)}
                className="relative group aspect-square border border-[#C8CCD1] rounded-lg overflow-hidden hover:border-[#3366CC] transition-colors"
              >
                <img
                  src={file.data}
                  alt={file.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="text-white text-sm">Вставить</span>
                </div>
              </button>
            ))}
          </div>
          
          {uploadedFiles.length === 0 && (
            <p className="text-center text-[#54595D] py-8">
              Нет загруженных изображений
            </p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
