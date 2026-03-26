'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  index?: number;
}

export function FeatureCard({ icon, title, description, index = 0 }: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      viewport={{ once: true }}
      className="glass-effect p-6 rounded-lg hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 group"
    >
      <div className="mb-4 p-3 bg-primary/10 rounded-lg w-fit group-hover:bg-primary/20 transition-colors">
        <div className="text-primary text-2xl">
          {icon}
        </div>
      </div>
      <h3 className="text-lg font-semibold mb-2 text-foreground">
        {title}
      </h3>
      <p className="text-foreground/60 text-sm leading-relaxed">
        {description}
      </p>
    </motion.div>
  );
}
