export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full border-t border-border bg-card/50 mt-auto">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-8">
          <div className="max-w-xs">
            <h3 className="font-bold text-xl text-primary mb-3">MatExtractAI</h3>
            <p className="text-foreground/60 text-sm leading-relaxed">
              Accelerating materials research by automating the extraction of high-fidelity data from scientific literature using advanced AI orchestration.
            </p>
          </div>
          <div className="flex gap-16">
            <div>
              <h4 className="font-semibold mb-4 text-foreground">Platform</h4>
              <ul className="space-y-3 text-sm text-foreground/60">
                <li><a href="/" className="hover:text-primary transition-colors">Home</a></li>
                <li><a href="/upload" className="hover:text-primary transition-colors">Process Document</a></li>
                <li><a href="/results" className="hover:text-primary transition-colors">Data Archive</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-foreground">Support</h4>
              <ul className="space-y-3 text-sm text-foreground/60">
                <li><a href="#" className="hover:text-primary transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Usage Terms</a></li>
                <li><a href="mailto:support@matextract.ai" className="hover:text-primary transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="border-t border-border/40 pt-8 flex flex-col md:flex-row justify-between items-center bg-transparent">
          <p className="text-foreground/50 text-xs">
            © {currentYear} MatExtractAI. Built for Scientific Excellence.
          </p>
          <div className="flex gap-6 mt-4 md:mt-0 text-xs text-foreground/50 uppercase tracking-widest">
            <span>Enterprise Grade</span>
            <span>•</span>
            <span>AI Powered</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
