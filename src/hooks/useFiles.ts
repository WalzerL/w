import { useState, useCallback } from 'react';
import type { UploadedFile, User } from '@/types';
import { getFiles, saveFile, deleteFile, getFileById } from '@/utils/storage';
import { generateId } from '@/utils/crypto';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'image/svg+xml',
  'application/pdf',
  'text/plain',
  'text/markdown',
];

export interface FileUploadResult {
  success: boolean;
  file?: UploadedFile;
  error?: string;
}

export function useFiles() {
  const [isUploading, setIsUploading] = useState(false);

  const getAllFiles = useCallback((): UploadedFile[] => {
    return getFiles();
  }, []);

  const getFile = useCallback((id: string): UploadedFile | null => {
    return getFileById(id);
  }, []);

  const uploadFile = useCallback(async (
    file: File,
    user: User
  ): Promise<FileUploadResult> => {
    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return {
        success: false,
        error: `Неподдерживаемый тип файла. Разрешены: изображения (JPEG, PNG, GIF, WebP, SVG), PDF, текстовые файлы`
      };
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return {
        success: false,
        error: `Файл слишком большой. Максимальный размер: 5MB`
      };
    }

    setIsUploading(true);

    try {
      // Convert file to base64
      const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      const uploadedFile: UploadedFile = {
        id: generateId(),
        name: file.name,
        type: file.type,
        data: base64,
        uploadedAt: Date.now(),
        uploadedBy: user.id,
      };

      saveFile(uploadedFile);

      return { success: true, file: uploadedFile };
    } catch {
      return { success: false, error: 'Ошибка при загрузке файла' };
    } finally {
      setIsUploading(false);
    }
  }, []);

  const uploadMultipleFiles = useCallback(async (
    files: FileList,
    user: User
  ): Promise<FileUploadResult[]> => {
    const results: FileUploadResult[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const result = await uploadFile(files[i], user);
      results.push(result);
    }
    
    return results;
  }, [uploadFile]);

  const removeFile = useCallback((id: string): boolean => {
    try {
      deleteFile(id);
      return true;
    } catch {
      return false;
    }
  }, []);

  const getImageFiles = useCallback((): UploadedFile[] => {
    return getFiles().filter(f => f.type.startsWith('image/'));
  }, []);

  const insertImageIntoMarkdown = useCallback((file: UploadedFile, altText?: string): string => {
    return `![${altText || file.name}](${file.data})`;
  }, []);

  return {
    isUploading,
    getAllFiles,
    getFile,
    uploadFile,
    uploadMultipleFiles,
    removeFile,
    getImageFiles,
    insertImageIntoMarkdown,
  };
}
