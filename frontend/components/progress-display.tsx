'use client';

import { motion } from 'framer-motion';
import { CheckCircle, Clock, Zap } from 'lucide-react';

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
  const isProcessing = status === 'processing';
  const isComplete = status === 'complete';

  return (
    <div className="w-full space-y-6">
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-foreground">Processing</h3>
          <span className="text-sm text-foreground/60">{progress}%</span>
        </div>
        <div className="relative h-3 bg-card rounded-full overflow-hidden border border-border">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-accent"
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Status Indicator */}
      <div className="flex items-center gap-3">
        {isComplete && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 20 }}
          >
            <CheckCircle className="w-5 h-5 text-green-500" />
          </motion.div>
        )}
        {isProcessing && (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          >
            <Zap className="w-5 h-5 text-primary" />
          </motion.div>
        )}
        {status === 'idle' && (
          <Clock className="w-5 h-5 text-foreground/50" />
        )}
        <span className="text-foreground text-sm font-medium">
          {isComplete
            ? 'Processing complete!'
            : isProcessing
            ? 'Processing...'
            : 'Ready to process'}
        </span>
      </div>

      {/* Current Step */}
      <div className="glass-effect p-4 rounded-lg">
        <p className="text-sm text-foreground/70">
          <span className="text-foreground/50">Current step: </span>
          <span className="text-foreground font-medium">{currentStep}</span>
        </p>
      </div>

      {/* Time Remaining */}
      {timeRemaining > 0 && isProcessing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-2 text-sm text-foreground/60"
        >
          <Clock className="w-4 h-4" />
          <span>Estimated time remaining: {Math.ceil(timeRemaining)}s</span>
        </motion.div>
      )}
    </div>
  );
}
