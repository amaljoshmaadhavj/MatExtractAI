'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { FileUp, Zap, BarChart3, ShieldCheck, ArrowRight, Layers, Database, FlaskConical, Search, FileText, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';

const features = [
  {
    icon: <Search className="w-5 h-5" />,
    title: 'Precise Extraction',
    description: 'Advanced parsing for multi-column layouts and scientific tables with high fidelity.',
  },
  {
    icon: <Database className="w-5 h-5" />,
    title: 'Structured Results',
    description: 'Convert research into standardized JSON or CSV formats ready for database ingestion.',
  },
  {
    icon: <FileText className="w-5 h-5" />,
    title: 'Contextual Analysis',
    description: 'Maintain the link between extracted data points and their original source context.',
  },
  {
    icon: <ShieldCheck className="w-5 h-5" />,
    title: 'Secure Processing',
    description: 'Built for enterprise-grade privacy, ensuring research data remains protected.',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header />
      
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="relative pt-24 pb-32 md:pt-40 md:pb-56 border-b border-border/50">
          <div className="subtle-grid absolute inset-0 -z-10 opacity-20" />
          
          <div className="container mx-auto px-6 max-w-5xl text-center">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full bg-secondary border border-border text-[10px] font-bold tracking-widest text-muted-foreground uppercase"
            >
              Enterprise-Grade Materials Informatics
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="text-4xl md:text-6xl font-bold tracking-tight mb-8 text-foreground text-balance leading-[1.1]"
            >
              Systematic Extraction for <br/>
              Materials Research.
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed font-medium"
            >
              A specialized analytical platform designed to automate the extraction of high-fidelity 
              data from scientific literature with precision and speed.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-3 justify-center items-center"
            >
              <Link href="/upload">
                <Button size="lg" className="h-12 px-8 rounded-lg">
                  Start Extraction <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="h-12 px-8 rounded-lg">
                View Documentation
              </Button>
            </motion.div>
          </div>
        </section>

        {/* Feature Grid */}
        <section className="py-24 md:py-32 bg-secondary/20">
          <div className="container mx-auto px-6 max-w-6xl">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="professional-card border-border/40"
                >
                  <div className="w-10 h-10 bg-primary/5 text-primary flex items-center justify-center rounded-lg mb-6 border border-primary/10">
                    {feature.icon}
                  </div>
                  <h3 className="font-bold text-base mb-2 text-foreground">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Workflow Section */}
        <section className="py-24 md:py-40">
          <div className="container mx-auto px-6 max-w-6xl">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
              <div>
                <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground mb-6 leading-tight">
                  From Literature to <br/>
                  Actionable Data.
                </h2>
                <p className="text-lg text-muted-foreground mb-10 leading-relaxed font-medium">
                  Our pipeline is engineered for the rigor of scientific research, ensuring 
                  every data point is validated and contextualized.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    'PDF Layout Analysis',
                    'Table Normalization',
                    'Unit Conversion',
                    'Source Linkage'
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-3 text-sm font-semibold text-foreground/80">
                      <CheckCircle2 className="w-4 h-4 text-primary" />
                      {item}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-0 bg-secondary/10 p-8 md:p-12 rounded-2xl border border-border/50">
                {[
                  { title: 'Data Ingestion', desc: 'Secure upload and automated decoding of scientific layouts.' },
                  { title: 'Deep Analysis', desc: 'Contextual extraction of mechanical and compositional properties.' },
                  { title: 'Validation', desc: 'Automated verification against scientific domain constraints.' },
                  { title: 'Structured Output', desc: 'Clean export in research-ready formats for further modeling.' }
                ].map((item, idx) => (
                  <div key={idx} className="workflow-step">
                    <h4 className="font-bold text-base text-foreground mb-1">{item.title}</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="pb-32 container mx-auto px-6 max-w-5xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="bg-primary p-12 md:p-20 rounded-3xl text-center text-primary-foreground shadow-sm"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6 tracking-tight">
              Ready to automate your data workflow?
            </h2>
            <p className="text-primary-foreground/70 mb-10 text-lg max-w-xl mx-auto font-medium">
              Join research teams accelerating materials discovery with systematic data extraction.
            </p>
            <Link href="/upload">
              <Button size="lg" variant="secondary" className="h-12 px-10 rounded-lg font-bold">
                Get Started
              </Button>
            </Link>
          </motion.div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}

