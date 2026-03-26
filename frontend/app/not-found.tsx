'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { PageContainer } from '@/components/page-container';

export default function NotFound() {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-card via-background to-background">
      <Header />
      <PageContainer className="flex flex-col items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <motion.h1
            className="text-9xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-4"
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            404
          </motion.h1>

          <h2 className="text-3xl font-bold mb-2">Page Not Found</h2>
          <p className="text-foreground/60 mb-8 max-w-md">
            The page you're looking for doesn't exist. Let's get you back on track.
          </p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link href="/">
              <Button size="lg">
                Back to Home
              </Button>
            </Link>
            <Link href="/upload">
              <Button size="lg" variant="outline">
                Upload PDF
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </PageContainer>
      <Footer />
    </div>
  );
}
