import Link from 'next/link';
import { FlaskConical, Github, Twitter, Linkedin } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-background border-t border-border/50 py-16 md:py-24">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="md:col-span-2">
            <Link href="/" className="flex items-center gap-2.5 mb-6 group">
              <div className="w-8 h-8 bg-primary flex items-center justify-center rounded-lg shadow-sm">
                <FlaskConical className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-bold text-lg text-foreground tracking-tight">MatExtract</span>
            </Link>
            <p className="text-muted-foreground text-sm leading-relaxed max-w-xs font-medium">
              Precision analytical platform for high-fidelity extraction of scientific data from research literature.
            </p>
          </div>
          
          <div>
            <h4 className="font-bold text-sm text-foreground mb-6 uppercase tracking-wider">Platform</h4>
            <ul className="space-y-4">
              {['Overview', 'Extract', 'Archive', 'Documentation'].map((item) => (
                <li key={item}>
                  <Link href="#" className="text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors">
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="font-bold text-sm text-foreground mb-6 uppercase tracking-wider">Connect</h4>
            <div className="flex gap-4">
              {[
                { icon: <Github className="w-5 h-5" />, label: 'GitHub' },
                { icon: <Twitter className="w-5 h-5" />, label: 'Twitter' },
                { icon: <Linkedin className="w-5 h-5" />, label: 'LinkedIn' }
              ].map((social) => (
                <Link 
                  key={social.label}
                  href="#" 
                  className="w-10 h-10 flex items-center justify-center rounded-lg bg-secondary text-muted-foreground hover:bg-primary hover:text-primary-foreground transition-all"
                  aria-label={social.label}
                >
                  {social.icon}
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        <div className="mt-16 pt-8 border-t border-border/50 flex flex-col md:flex-row justify-between items-center gap-6">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
            © {new Date().getFullYear()} MatExtract AI. All rights reserved.
          </p>
          <div className="flex gap-8">
            <Link href="#" className="text-xs font-bold text-muted-foreground hover:text-foreground uppercase tracking-widest">Privacy Policy</Link>
            <Link href="#" className="text-xs font-bold text-muted-foreground hover:text-foreground uppercase tracking-widest">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
