'use client';

import { useState, useEffect, Suspense } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ArrowLeft, X, Loader } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { PageContainer } from '@/components/page-container';
import { ProgressDisplay } from '@/components/progress-display';
import { getJobStatus } from '@/lib/api-client';

function ProgressContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get('jobId');

  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'processing' | 'completed'>('processing');
  const [currentStep, setCurrentStep] = useState('Initializing...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setError('No job ID provided');
      return;
    }

    const checkProgress = async () => {
      try {
        const data = await getJobStatus(jobId);
        setProgress(data.progress || 0);
        setStatus(data.status as 'processing' | 'completed');
        setCurrentStep(data.current_step || 'Processing...');
        if (data.status === 'completed') {
          setProgress(100);
        }
      } catch (err) {
        console.error('Error fetching job status:', err);
      }
    };

    // Check progress every 1 second for real-time updates
    const interval = setInterval(checkProgress, 1000);

    // Initial check
    checkProgress();

    return () => clearInterval(interval);
  }, [jobId]);

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
            <Link href="/upload" className="inline-flex items-center gap-2 text-primary hover:text-accent transition-colors mb-4">
              <ArrowLeft className="w-4 h-4" />
              Back to Upload
            </Link>
            <h1 className="text-4xl font-bold mb-2">Processing Document</h1>
            <p className="text-foreground/70">
              Your PDF is being analyzed. This typically takes 30-60 seconds.
            </p>
          </div>

          {/* Error State */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-effect p-6 rounded-lg mb-8 text-red-500"
            >
              <p>{error}</p>
              <Link href="/upload" className="inline-block mt-4">
                <Button variant="outline">Upload a Document</Button>
              </Link>
            </motion.div>
          )}

          {/* Progress Display */}
          {!error && (
            <div className="mb-12">
              <ProgressDisplay
                progress={Math.round(progress)}
                currentStep={currentStep}
              />
            </div>
          )}

          {/* Status Section */}
          <div className="glass-effect p-6 rounded-lg mb-8">
            <h2 className="text-lg font-semibold mb-4">Status</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-foreground/70">Current Progress:</span>
                <span className="font-semibold">{progress}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-foreground/70">Current Step:</span>
                <span className="font-semibold">{currentStep}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-foreground/70">Status:</span>
                <span className="font-semibold capitalize">{status}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            {status === 'completed' && jobId && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="flex gap-3 w-full"
              >
                <Link href={`/results?jobId=${jobId}`} className="flex-1">
                  <Button size="lg" className="w-full">
                    View Results
                  </Button>
                </Link>
                <Link href="/upload" className="flex-1">
                  <Button size="lg" variant="outline" className="w-full">
                    Upload Another
                  </Button>
                </Link>
              </motion.div>
            )}
            {status === 'processing' && (
              <Button variant="outline" size="lg" className="gap-2 w-full">
                <Loader className="w-4 h-4 animate-spin" />
                Processing...
              </Button>
            )}
          </div>

          {/* Info Section */}
          <div className="mt-12 pt-8 border-t border-border">
            <h3 className="text-lg font-semibold mb-4 text-foreground">
              What's happening?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">1. Analysis</h4>
                <p className="text-foreground/60 text-sm">
                  PDF structure is analyzed and material sections identified
                </p>
              </div>
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">2. Extraction</h4>
                <p className="text-foreground/60 text-sm">
                  AI models extract properties, composition, and experimental data
                </p>
              </div>
              <div className="glass-effect p-4 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">3. Validation</h4>
                <p className="text-foreground/60 text-sm">
                  Extracted data is validated and formatted for display
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

export default function ProgressPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-8 h-8 animate-spin text-primary" />
      </div>
    }>
      <ProgressContent />
    </Suspense>
  );
}
