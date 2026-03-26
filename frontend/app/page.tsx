'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { FileUp, Zap, BarChart3, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { PageContainer } from '@/components/page-container';
import { FeatureCard } from '@/components/feature-card';

const features = [
  {
    icon: <FileUp className="w-6 h-6" />,
    title: 'Smart PDF Upload',
    description: 'Drag and drop your scientific papers and let our AI analyze them instantly.',
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: 'AI-Powered Extraction',
    description: 'Advanced machine learning models extract material data with precision.',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: 'Rich Visualizations',
    description: 'View extracted data in interactive charts and detailed tables.',
  },
  {
    icon: <Lock className="w-6 h-6" />,
    title: 'Secure & Private',
    description: 'Your documents are processed securely and never stored permanently.',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-card via-background to-background">
      <Header />
      <PageContainer className="flex-grow">
        {/* Hero Section */}
        <section className="relative mb-16 md:mb-24">
          <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute w-96 h-96 bg-primary/5 rounded-full blur-3xl -top-40 -right-40" />
            <div className="absolute w-96 h-96 bg-accent/5 rounded-full blur-3xl -bottom-40 -left-40" />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-4 text-balance">
              Extract Material Data
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent"> with AI</span>
            </h1>
            <p className="text-lg md:text-xl text-foreground/70 max-w-2xl mx-auto text-balance">
              MatExtractAI intelligently analyzes scientific papers and extracts material properties, composition data, and experimental results automatically.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
          >
            <Link href="/upload" className="w-full sm:w-auto">
              <Button size="lg" className="w-full">
                Get Started
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="w-full sm:w-auto">
              Learn More
            </Button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-3 gap-4 mb-12"
          >
            {[
              { label: 'Papers Processed', value: '10K+', color: 'text-primary' },
              { label: 'Accuracy Rate', value: '99.8%', color: 'text-accent' },
              { label: 'Availability', value: '24/7', color: 'text-primary' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
              >
                <p className={`text-2xl md:text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                <p className="text-foreground/60 text-sm">{stat.label}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="mb-20 md:mb-32">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-foreground">
              Powerful Features
            </h2>
            <p className="text-foreground/60 text-lg max-w-2xl mx-auto">
              Everything you need to extract and analyze material data efficiently.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <FeatureCard key={index} {...feature} index={index} />
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="glass-effect p-8 md:p-12 rounded-lg text-center border border-primary/20"
          >
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-foreground/70 mb-6 text-lg">
              Upload your first document and see how MatExtractAI can streamline your research.
            </p>
            <Link href="/upload" className="inline-block">
              <Button size="lg">
                Upload PDF Now
              </Button>
            </Link>
          </motion.div>
        </section>
      </PageContainer>
      <Footer />
    </div>
  );
}
