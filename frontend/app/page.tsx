'use client';

import * as React from 'react';
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
  const [mousePos, setMousePos] = React.useState({ x: '50%', y: '50%' });

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({
      x: `${e.clientX - rect.left}px`,
      y: `${e.clientY - rect.top}px`,
    });
  };

  return (
    <div 
      className="flex flex-col min-h-screen bg-background selection:bg-primary/10"
      onMouseMove={handleMouseMove}
      style={{ '--mouse-x': mousePos.x, '--mouse-y': mousePos.y } as React.CSSProperties}
    >
      <Header />
      <PageContainer className="flex-grow pt-12 md:pt-20">
        {/* Hero Section */}
        <section className="relative mb-24 md:mb-32 scientific-grid bg-fixed hero-glow">
          <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background -z-10" />
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-center mb-16 px-4"
          >
            <div className="inline-block px-4 py-1.5 mb-8 rounded-full bg-primary/5 border border-primary/20 text-xs font-semibold tracking-widest text-primary uppercase">
              Domain-Specific AI Orchestration
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight text-foreground uppercase">
              Accelerate Materials <br/>
              <span className="text-primary border-l-4 border-primary pl-4 inline-block mt-1">Informatics.</span>
            </h1>
            <p className="text-xl text-foreground/60 max-w-2xl mx-auto leading-relaxed font-medium">
              A specialized multi-agent platform for high-fidelity extraction of structural, mechanical, and compositional data from scientific literature.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-5 justify-center mb-24"
          >
            <Link href="/upload">
              <Button size="lg" className="h-14 px-10 text-base font-semibold shadow-xl shadow-primary/20">
                Begin Extraction
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="h-14 px-10 text-base font-semibold border-2">
              Platform Overview
            </Button>
          </motion.div>

          {/* Technical Milestones */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto border-t border-border pt-16"
          >
            {[
              { title: 'Automated Ingestion', desc: 'Neural parsing of multi-column PDF layouts and embedded tables.', color: 'text-primary' },
              { title: 'Multi-Agent Logic', desc: 'Specialized sub-agents for Mechanical vs. Compositional validation.', color: 'text-primary' },
              { title: 'Local Infrastructure', desc: 'Secure local model execution with zero-retention data policies.', color: 'text-primary' },
            ].map((strength, index) => (
              <div key={index} className="px-4">
                <h4 className="text-base font-bold mb-3 tracking-tight text-foreground">{strength.title}</h4>
                <p className="text-sm text-foreground/50 leading-relaxed font-medium">{strength.desc}</p>
              </div>
            ))}
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="mb-32">
          <div className="flex flex-col md:flex-row items-end justify-between mb-16 gap-4">
            <div className="max-w-xl text-left">
              <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground mb-4">
                Built for the Modern Lab.
              </h2>
              <p className="text-lg text-foreground/50 font-medium">
                Streamline your data pipeline with features designed for materials scientists.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <FeatureCard key={index} {...feature} index={index} />
            ))}
          </div>
        </section>

        {/* Workflow Section */}
        <section className="mb-32 max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-extrabold tracking-tight text-foreground mb-4">
              The Analytical Pipeline.
            </h2>
            <p className="text-foreground/50 font-medium">
              From raw scientific literature to structured materials datasets.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 px-4">
            {[
              { step: '01', title: 'Ingestion', desc: 'Secure upload and layout-aware PDF decoding.' },
              { step: '02', title: 'Orchestration', desc: 'Multi-agent analysis of text, tables, and images.' },
              { step: '03', title: 'Validation', desc: 'Cross-referencing data points for scientific accuracy.' },
              { step: '04', title: 'Export', desc: 'Structured JSON/CSV output for research workflows.' }
            ].map((item, idx) => (
              <div key={idx} className="workflow-step group">
                <span className="text-[10px] font-bold text-primary uppercase tracking-widest block mb-2 opacity-50 group-hover:opacity-100 transition-opacity">
                  Phase {item.step}
                </span>
                <h4 className="font-bold text-foreground mb-2">{item.title}</h4>
                <p className="text-sm text-foreground/50 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="mb-16">
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="p-12 md:p-20 rounded-2xl text-center bg-primary/[0.02] border border-primary/10 relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-[100px] -mr-32 -mt-32" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-primary/5 rounded-full blur-[100px] -ml-32 -mb-32" />
            
            <h2 className="text-3xl md:text-5xl font-extrabold mb-6 tracking-tight">
              Ready to automate your <br/>
              <span className="text-primary italic">Literature Review?</span>
            </h2>
            <p className="text-foreground/60 mb-10 text-lg max-w-xl mx-auto font-medium">
              Join research labs accelerating discovery with structured data extraction.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/upload">
                <Button size="lg" className="h-14 px-12 text-base font-bold shadow-2xl shadow-primary/20 hover:scale-105 transition-transform">
                  Get Started Locally
                </Button>
              </Link>
            </div>
          </motion.div>
        </section>
      </PageContainer>
      <Footer />
    </div>
  );
}
