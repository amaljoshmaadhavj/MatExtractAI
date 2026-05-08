'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, AlertCircle, CheckCircle2, FileText, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FileUploadZoneProps {
  onFileSelect?: (file: File | null) => void;
  selectedFile?: File | null;
}

export function FileUploadZone({ onFileSelect, selectedFile }: FileUploadZoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File) => {
    if (file.type !== 'application/pdf') {
      setError('Please upload a valid scientific PDF document');
      return false;
    }
    if (file.size > 25 * 1024 * 1024) {
      setError('Document size exceeds the 25MB limit');
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
        animate={isDragActive ? { y: -2 } : { y: 0 }}
        className={`relative border-2 border-dashed rounded-xl p-10 md:p-16 transition-all duration-200 cursor-pointer text-center ${
          isDragActive
            ? 'border-primary bg-primary/5'
            : selectedFile
            ? 'border-primary/40 bg-secondary/20'
            : 'border-border hover:border-primary/50 hover:bg-secondary/10'
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

        <div className="flex flex-col items-center justify-center gap-4">
          {selectedFile ? (
            <>
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <p className="font-bold text-foreground text-sm">Document Ready</p>
                <div className="flex items-center gap-2 mt-2 justify-center text-muted-foreground text-xs font-semibold">
                  <FileText className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[200px]">{selectedFile.name}</span>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center text-muted-foreground">
                <Upload className="w-6 h-6" />
              </div>
              <div>
                <p className="font-bold text-foreground text-sm">
                  Click or drag document to upload
                </p>
                <p className="text-muted-foreground text-xs mt-2 font-medium">
                  Scientific PDF documents up to 25MB
                </p>
              </div>
            </>
          )}
        </div>

        {selectedFile && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 h-8 w-8 rounded-lg hover:bg-background"
            onClick={(e) => {
              e.stopPropagation();
              onFileSelect?.(null);
            }}
          >
            <X className="w-4 h-4 text-muted-foreground" />
          </Button>
        )}
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 flex items-center gap-2 text-destructive text-xs font-bold uppercase tracking-wider justify-center"
        >
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </motion.div>
      )}
    </div>
  );
}

