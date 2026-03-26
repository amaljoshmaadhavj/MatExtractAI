import { ReactNode } from 'react';

interface PageContainerProps {
  children: ReactNode;
  className?: string;
}

export function PageContainer({ children, className = '' }: PageContainerProps) {
  return (
    <div className={`min-h-screen flex flex-col ${className}`}>
      <div className="container mx-auto px-4 py-8 md:py-12 max-w-7xl flex-grow">
        {children}
      </div>
    </div>
  );
}
