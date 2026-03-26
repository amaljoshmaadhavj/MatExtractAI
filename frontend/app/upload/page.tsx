'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, FileUp, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { PageContainer } from '@/components/page-container';
import { FileUploadZone } from '@/components/file-upload-zone';
import { uploadPDF } from '@/lib/api-client';

export default function UploadPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File | null) => {
    if (file === null) {
      setSelectedFile(null);
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);
    try {
      const response = await uploadPDF(selectedFile);
      // Redirect to progress page with job ID
      router.push(`/progress?jobId=${response.job_id}`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      console.error('Upload error:', error);
      setError(errorMessage);
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-card via-background to-background">
      <Header />
      <PageContainer>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto"
        >
          {/* Header */}
          <div className="mb-8">
            <Link href="/" className="inline-flex items-center gap-2 text-primary hover:text-accent transition-colors mb-4">
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
            <h1 className="text-4xl font-bold mb-2">Upload PDF</h1>
            <p className="text-foreground/70">
              Select a scientific paper to analyze and extract material data
            </p>
          </div>

          {/* Upload Zone */}
          <div className="mb-12">
            <FileUploadZone
              selectedFile={selectedFile}
              onFileSelect={handleFileSelect}
            />
          </div>

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 mb-8 flex gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-600 mb-1">Upload Error</h4>
                <p className="text-red-600/80 text-sm">{error}</p>
              </div>
            </motion.div>
          )}

          {/* File Info */}
          {selectedFile && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-effect p-6 rounded-lg mb-8"
            >
              <h3 className="font-semibold mb-4 text-foreground">File Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-foreground/60">Filename:</span>
                  <span className="text-foreground font-medium truncate">{selectedFile.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-foreground/60">File Size:</span>
                  <span className="text-foreground font-medium">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-foreground/60">Type:</span>
                  <span className="text-foreground font-medium">{selectedFile.type}</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Upload Button */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="flex gap-3"
          >
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || isProcessing}
              size="lg"
              className="flex-1 gap-2"
            >
              {isProcessing ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <FileUp className="w-5 h-5" />
                  </motion.div>
                  Processing...
                </>
              ) : (
                <>
                  <FileUp className="w-5 h-5" />
                  Start Extraction
                </>
              )}
            </Button>
            {selectedFile && (
              <Button
                variant="outline"
                size="lg"
                onClick={() => setSelectedFile(null)}
                disabled={isProcessing}
              >
                Clear
              </Button>
            )}
          </motion.div>

          {/* Info Section */}
          <div className="mt-12 pt-8 border-t border-border">
            <h3 className="text-lg font-semibold mb-4 text-foreground">
              What data can we extract?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">Material Properties</h4>
                <p className="text-foreground/60 text-sm">
                  Density, melting point, tensile strength, and thermal properties
                </p>
              </div>
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">Composition Data</h4>
                <p className="text-foreground/60 text-sm">
                  Element percentages, doping levels, and chemical formulas
                </p>
              </div>
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">Experimental Results</h4>
                <p className="text-foreground/60 text-sm">
                  Test conditions, measurements, and performance metrics
                </p>
              </div>
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">Synthesis Methods</h4>
                <p className="text-foreground/60 text-sm">
                  Processing techniques and parameters used in research
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </PageContainer>
      <Footer />
    </div>
  );
}
