'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, AlertCircle, CheckCircle, File } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FileUploadZoneProps {
  onFileSelect?: (file: File) => void;
  selectedFile?: File | null;
}

export function FileUploadZone({ onFileSelect, selectedFile }: FileUploadZoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File) => {
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return false;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      return false;
    }
    setError(null);
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files?.[0]) {
      if (validateFile(files[0])) {
        onFileSelect?.(files[0]);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files?.[0]) {
      if (validateFile(files[0])) {
        onFileSelect?.(files[0]);
      }
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className="w-full">
      <motion.div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        animate={isDragActive ? { scale: 0.98 } : { scale: 1 }}
        className={`relative border-2 border-dashed rounded-lg p-8 md:p-12 transition-all duration-200 cursor-pointer ${
          isDragActive
            ? 'border-primary bg-primary/5'
            : selectedFile
            ? 'border-green-500/50 bg-green-500/5'
            : 'border-border hover:border-primary/50 hover:bg-primary/5'
        }`}
        onClick={handleClick}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="hidden"
          aria-label="Upload PDF file"
        />

        <div className="flex flex-col items-center justify-center gap-3">
          {selectedFile ? (
            <>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                className="text-green-500"
              >
                <CheckCircle className="w-12 h-12" />
              </motion.div>
              <div className="text-center">
                <p className="font-semibold text-foreground">File Selected</p>
                <div className="flex items-center gap-2 mt-2 justify-center text-foreground/60 text-sm">
                  <File className="w-4 h-4" />
                  <span className="truncate max-w-xs">{selectedFile.name}</span>
                </div>
                <p className="text-xs text-foreground/50 mt-1">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </>
          ) : (
            <>
              <motion.div
                animate={isDragActive ? { y: -5 } : { y: 0 }}
                transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                className="text-primary"
              >
                <Upload className="w-12 h-12" />
              </motion.div>
              <div className="text-center">
                <p className="font-semibold text-foreground">
                  Drag and drop your PDF here
                </p>
                <p className="text-foreground/60 text-sm mt-1">
                  or click to browse your computer
                </p>
                <p className="text-xs text-foreground/50 mt-2">
                  Max file size: 50MB
                </p>
              </div>
            </>
          )}
        </div>

        {selectedFile && (
          <Button
            variant="outline"
            size="sm"
            className="absolute top-3 right-3"
            onClick={(e) => {
              e.stopPropagation();
              onFileSelect?.(null);
            }}
          >
            Clear
          </Button>
        )}
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 flex items-center gap-2 text-destructive text-sm"
        >
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </motion.div>
      )}
    </div>
  );
}
