'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import Link from 'next/link';
import { Moon, Sun, Menu, X, FlaskConical } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  const { theme, setTheme } = useTheme();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-md">
      <div className="container mx-auto px-6 max-w-7xl h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 bg-primary flex items-center justify-center rounded-lg shadow-sm">
            <FlaskConical className="w-4 h-4 text-primary-foreground" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base text-foreground tracking-tight leading-none">MatExtract</span>
            <span className="text-[9px] uppercase tracking-[0.2em] font-bold text-muted-foreground mt-1">Research AI</span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {[
            { label: 'Overview', href: '/' },
            { label: 'Extract', href: '/upload' },
            { label: 'Archive', href: '/results' }
          ].map((link) => (
            <Link 
              key={link.label}
              href={link.href} 
              className="text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="rounded-lg h-9 w-9 text-muted-foreground hover:text-foreground"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="md:hidden rounded-lg h-9 w-9"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="h-4 w-4" />
            ) : (
              <Menu className="h-4 w-4" />
            )}
          </Button>
          
          <Link href="/upload" className="hidden md:block">
            <Button size="sm" className="rounded-lg font-bold px-5 h-9">Get Started</Button>
          </Link>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <nav className="md:hidden border-t border-border/50 bg-background p-6 flex flex-col gap-4 animate-in slide-in-from-top-2 duration-200">
          {[
            { label: 'Overview', href: '/' },
            { label: 'Extract', href: '/upload' },
            { label: 'Archive', href: '/results' }
          ].map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="text-sm font-bold text-muted-foreground hover:text-foreground py-2"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <Link href="/upload" onClick={() => setIsMobileMenuOpen(false)}>
            <Button className="w-full rounded-lg font-bold h-10 mt-2">Get Started</Button>
          </Link>
        </nav>
      )}
    </header>
  );
}

