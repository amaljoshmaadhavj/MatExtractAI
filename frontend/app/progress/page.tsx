'use client';

import { useState, useEffect, Suspense } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ArrowLeft, X, Loader2, CheckCircle2, ShieldCheck, Database, FlaskConical } from 'lucide-react';
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

    const interval = setInterval(checkProgress, 1000);
    checkProgress();
    return () => clearInterval(interval);
  }, [jobId]);

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
            <Link href="/upload" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary transition-colors mb-6">
              <ArrowLeft className="w-4 h-4" />
              Back to Upload
            </Link>
            <h1 className="text-3xl font-bold tracking-tight mb-3">Analysis in Progress</h1>
            <p className="text-muted-foreground font-medium">
              Our pipeline is systematically extracting data from your document.
            </p>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-destructive/5 border border-destructive/20 rounded-xl p-8 mb-8 text-center">
              <p className="text-destructive font-bold mb-6">{error}</p>
              <Link href="/upload">
                <Button variant="outline" className="rounded-lg">Return to Upload</Button>
              </Link>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            <div className="lg:col-span-2 space-y-6">
              {/* Progress Display */}
              {!error && (
                <div className="bg-card border border-border rounded-xl p-8 shadow-sm">
                  <ProgressDisplay
                    progress={Math.round(progress)}
                    currentStep={currentStep}
                  />
                </div>
              )}

              {/* Status Section */}
              <div className="professional-card">
                <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground mb-6">Pipeline Status</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-border/50">
                    <span className="text-sm font-medium text-muted-foreground">Completion Rate</span>
                    <span className="text-sm font-bold">{progress}%</span>
                  </div>
                  <div className="flex items-center justify-between pb-3 border-b border-border/50">
                    <span className="text-sm font-medium text-muted-foreground">Active Step</span>
                    <span className="text-sm font-bold">{currentStep}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground">Orchestration Status</span>
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 text-[10px] text-primary font-bold uppercase tracking-wider">
                      {status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                {status === 'completed' && jobId && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex gap-3 w-full"
                  >
                    <Link href={`/results?jobId=${jobId}`} className="flex-1">
                      <Button size="lg" className="w-full h-12 rounded-lg font-bold shadow-sm">
                        View Results
                      </Button>
                    </Link>
                    <Link href="/upload" className="flex-1">
                      <Button size="lg" variant="outline" className="w-full h-12 rounded-lg font-bold">
                        Analyze Another
                      </Button>
                    </Link>
                  </motion.div>
                )}
                {status === 'processing' && (
                  <Button variant="outline" size="lg" className="gap-2 w-full h-12 rounded-lg font-bold cursor-wait opacity-80">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Extraction in Progress...
                  </Button>
                )}
              </div>
            </div>

            <aside className="space-y-6">
              <div className="professional-card bg-secondary/30">
                <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-4">Pipeline Logic</h3>
                <div className="space-y-6">
                  {[
                    { title: 'Extraction', icon: <FlaskConical className="w-4 h-4" />, desc: 'Converting raw PDF layouts into structured data formats.' },
                    { title: 'Normalization', icon: <Database className="w-4 h-4" />, desc: 'Standardizing units and chemical formulas across sources.' },
                    { title: 'Validation', icon: <ShieldCheck className="w-4 h-4" />, desc: 'Verifying data accuracy against scientific constraints.' }
                  ].map((step, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="mt-0.5 text-primary">{step.icon}</div>
                      <div>
                        <h4 className="text-xs font-bold mb-1">{step.title}</h4>
                        <p className="text-[10px] leading-relaxed text-muted-foreground font-medium">{step.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="professional-card">
                <p className="text-[10px] leading-relaxed text-muted-foreground font-medium italic">
                  Note: Complex documents with many tables may take up to 90 seconds for full extraction.
                </p>
              </div>
            </aside>
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
      <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    }>
      <ProgressContent />
    </Suspense>
  );
}

