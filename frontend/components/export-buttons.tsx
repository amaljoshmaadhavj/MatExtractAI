'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ExportButtonsProps {
  data: any;
  filename?: string;
}

export function ExportButtons({ data, filename = 'extraction-results' }: ExportButtonsProps) {
  const [copied, setCopied] = useState(false);
  const [exported, setExported] = useState<'json' | 'csv' | null>(null);

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleExportJSON = () => {
    try {
      const jsonString = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setExported('json');
      setTimeout(() => setExported(null), 2000);
    } catch (error) {
      console.error('Failed to export JSON:', error);
    }
  };

  const handleExportCSV = () => {
    try {
      let csvContent = '';

      if (Array.isArray(data)) {
        const headers = Object.keys(data[0] || {});
        csvContent = headers.join(',') + '\n';
        data.forEach((row: any) => {
          const values = headers.map((header) => {
            const value = row[header];
            if (typeof value === 'string' && value.includes(',')) {
              return `"${value}"`;
            }
            return value;
          });
          csvContent += values.join(',') + '\n';
        });
      } else {
        const headers = Object.keys(data);
        csvContent = headers.join(',') + '\n';
        csvContent += headers.map((h) => data[h]).join(',') + '\n';
      }

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setExported('csv');
      setTimeout(() => setExported(null), 2000);
    } catch (error) {
      console.error('Failed to export CSV:', error);
    }
  };

  return (
    <div className="flex flex-wrap gap-3">
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          onClick={handleCopyToClipboard}
          variant={copied ? 'default' : 'outline'}
          className="gap-2"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              Copy JSON
            </>
          )}
        </Button>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          onClick={handleExportJSON}
          variant={exported === 'json' ? 'default' : 'outline'}
          className="gap-2"
        >
          {exported === 'json' ? (
            <>
              <Check className="w-4 h-4" />
              Exported
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              JSON
            </>
          )}
        </Button>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          onClick={handleExportCSV}
          variant={exported === 'csv' ? 'default' : 'outline'}
          className="gap-2"
        >
          {exported === 'csv' ? (
            <>
              <Check className="w-4 h-4" />
              Exported
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              CSV
            </>
          )}
        </Button>
      </motion.div>
    </div>
  );
}
