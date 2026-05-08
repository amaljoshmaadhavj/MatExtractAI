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
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      viewport={{ once: true }}
      className="professional-card"
    >
      <div className="mb-6 p-3 bg-primary/10 rounded-xl w-fit text-primary group-hover:bg-primary/20 transition-colors">
        {icon}
      </div>
      <h3 className="text-base font-bold mb-2 text-foreground tracking-tight">
        {title}
      </h3>
      <p className="text-muted-foreground text-sm leading-relaxed font-medium">
        {description}
      </p>
    </motion.div>
  );
}

