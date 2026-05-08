'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Copy, Check, FileJson, Table } from 'lucide-react';
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
    <div className="flex flex-wrap gap-2">
      <Button
        onClick={handleCopyToClipboard}
        variant="outline"
        size="sm"
        className={`h-9 px-3 rounded-lg gap-2 text-xs font-bold uppercase tracking-wider transition-all ${
          copied ? 'bg-primary/10 border-primary text-primary hover:bg-primary/15' : ''
        }`}
      >
        {copied ? (
          <Check className="w-3.5 h-3.5" />
        ) : (
          <Copy className="w-3.5 h-3.5" />
        )}
        {copied ? 'Copied' : 'Copy'}
      </Button>

      <Button
        onClick={handleExportJSON}
        variant="outline"
        size="sm"
        className={`h-9 px-3 rounded-lg gap-2 text-xs font-bold uppercase tracking-wider transition-all ${
          exported === 'json' ? 'bg-primary/10 border-primary text-primary hover:bg-primary/15' : ''
        }`}
      >
        {exported === 'json' ? (
          <Check className="w-3.5 h-3.5" />
        ) : (
          <FileJson className="w-3.5 h-3.5" />
        )}
        JSON
      </Button>

      <Button
        onClick={handleExportCSV}
        variant="outline"
        size="sm"
        className={`h-9 px-3 rounded-lg gap-2 text-xs font-bold uppercase tracking-wider transition-all ${
          exported === 'csv' ? 'bg-primary/10 border-primary text-primary hover:bg-primary/15' : ''
        }`}
      >
        {exported === 'csv' ? (
          <Check className="w-3.5 h-3.5" />
        ) : (
          <Table className="w-3.5 h-3.5" />
        )}
        CSV
      </Button>
    </div>
  );
}

