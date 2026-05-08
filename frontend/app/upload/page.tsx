'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, FileUp, AlertCircle, Info, CheckCircle2, FileText } from 'lucide-react';
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
      router.push(`/progress?jobId=${response.job_id}`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      console.error('Upload error:', error);
      setError(errorMessage);
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header />
      <PageContainer>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <div className="mb-12">
            <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary transition-colors mb-6">
              <ArrowLeft className="w-4 h-4" />
              Back to Overview
            </Link>
            <h1 className="text-3xl font-bold tracking-tight mb-3">Extract Data</h1>
            <p className="text-muted-foreground font-medium">
              Upload a scientific publication to begin the systematic extraction process.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            <div className="lg:col-span-2 space-y-6">
              {/* Upload Zone */}
              <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
                <FileUploadZone
                  selectedFile={selectedFile}
                  onFileSelect={handleFileSelect}
                />
              </div>

              {/* Error Display */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-destructive/5 border border-destructive/20 rounded-xl p-4 flex gap-3"
                >
                  <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-destructive text-sm mb-1">Processing Error</h4>
                    <p className="text-destructive/80 text-xs font-medium">{error}</p>
                  </div>
                </motion.div>
              )}

              {/* Upload Button */}
              <div className="flex gap-3">
                <Button
                  onClick={handleUpload}
                  disabled={!selectedFile || isProcessing}
                  size="lg"
                  className="flex-1 h-12 gap-2 rounded-lg font-bold"
                >
                  {isProcessing ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      >
                        <FileUp className="w-4 h-4" />
                      </motion.div>
                      Initializing Pipeline...
                    </>
                  ) : (
                    <>
                      <FileUp className="w-4 h-4" />
                      Begin Systematic Extraction
                    </>
                  )}
                </Button>
                {selectedFile && (
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => setSelectedFile(null)}
                    disabled={isProcessing}
                    className="h-12 rounded-lg"
                  >
                    Reset
                  </Button>
                )}
              </div>
            </div>

            <aside className="space-y-6">
              {/* File Info */}
              {selectedFile ? (
                <motion.div
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="professional-card"
                >
                  <div className="flex items-center gap-2 mb-4 text-primary">
                    <FileText className="w-4 h-4" />
                    <h3 className="font-bold text-sm">Document Metadata</h3>
                  </div>
                  <div className="space-y-4 text-xs">
                    <div className="flex flex-col gap-1">
                      <span className="text-muted-foreground font-semibold uppercase tracking-wider">Filename</span>
                      <span className="text-foreground font-bold truncate">{selectedFile.name}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-y border-border/50">
                      <span className="text-muted-foreground font-semibold uppercase tracking-wider">Size</span>
                      <span className="text-foreground font-bold">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground font-semibold uppercase tracking-wider">Status</span>
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 text-primary font-bold">
                        Ready
                      </span>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="professional-card bg-secondary/30">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h3 className="font-bold text-sm mb-2">Requirements</h3>
                      <ul className="text-xs text-muted-foreground space-y-2 font-medium">
                        <li className="flex gap-2">
                          <CheckCircle2 className="w-3 h-3 text-primary shrink-0 mt-0.5" />
                          Scientific PDF format
                        </li>
                        <li className="flex gap-2">
                          <CheckCircle2 className="w-3 h-3 text-primary shrink-0 mt-0.5" />
                          Max file size 25MB
                        </li>
                        <li className="flex gap-2">
                          <CheckCircle2 className="w-3 h-3 text-primary shrink-0 mt-0.5" />
                          Clear table structures
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Capabilities */}
              <div className="professional-card">
                <h3 className="font-bold text-sm mb-4">Pipeline Capabilities</h3>
                <div className="space-y-3">
                  {[
                    { label: 'Mechanical Properties', value: 'Tensile, Hardness, etc.' },
                    { label: 'Compositional Data', value: 'Elemental %, Doping' },
                    { label: 'Synthesis Params', value: 'Temp, Pressure, Time' }
                  ].map((cap, i) => (
                    <div key={i} className="pb-3 border-b border-border/50 last:border-0 last:pb-0">
                      <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">{cap.label}</p>
                      <p className="text-xs font-semibold text-foreground/80">{cap.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </motion.div>
      </PageContainer>
      <Footer />
    </div>
  );
}

