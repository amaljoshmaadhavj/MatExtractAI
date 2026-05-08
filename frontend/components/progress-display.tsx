'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Clock, Loader2, Search } from 'lucide-react';

interface ProgressDisplayProps {
  progress?: number;
  status?: 'idle' | 'processing' | 'complete';
  timeRemaining?: number;
  currentStep?: string;
}

export function ProgressDisplay({
  progress = 0,
  status = 'idle',
  timeRemaining = 0,
  currentStep = 'Initializing...',
}: ProgressDisplayProps) {
  const isProcessing = status === 'processing' || (progress > 0 && progress < 100);
  const isComplete = status === 'complete' || progress === 100;

  return (
    <div className="w-full space-y-8">
      {/* Progress Bar Section */}
      <div className="space-y-3">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">Extraction Progress</h3>
            <p className="text-sm font-bold text-foreground">{isComplete ? 'Analysis Finalized' : 'Orchestrating Pipeline'}</p>
          </div>
          <span className="text-lg font-black text-primary tabular-nums">{progress}%</span>
        </div>
        <div className="relative h-2 bg-secondary rounded-full overflow-hidden border border-border/50">
          <motion.div
            className="h-full bg-primary"
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          />
        </div>
      </div>

      {/* Detail Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isComplete ? 'bg-primary/10 text-primary' : 'bg-background text-muted-foreground'}`}>
            {isComplete ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Clock className="w-4 h-4" />
            )}
          </div>
          <div>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Current Pipeline Task</p>
            <p className="text-sm font-bold text-foreground/90">{currentStep}</p>
          </div>
        </div>

        {timeRemaining > 0 && isProcessing && (
          <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-background text-muted-foreground">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Estimated Remaining</p>
              <p className="text-sm font-bold text-foreground/90">~{Math.ceil(timeRemaining)} seconds</p>
            </div>
          </div>
        )}
      </div>

      {/* Log-style feedback */}
      {!isComplete && (
        <div className="flex items-center gap-3 px-1">
          <Search className="w-3.5 h-3.5 text-primary animate-pulse" />
          <span className="text-[11px] font-medium text-muted-foreground italic">
            AI models are currently parsing materials tables and mechanical data...
          </span>
        </div>
      )}
    </div>
  );
}

