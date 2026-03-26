# MatExtractAI

A modern, AI-powered web application for extracting material data from scientific papers using advanced machine learning models.

## Features

- 📄 **Smart PDF Upload** - Drag and drop interface for uploading scientific papers
- 🤖 **AI-Powered Extraction** - Advanced ML models to extract material properties and experimental data
- 📊 **Rich Visualizations** - Interactive charts and detailed data tables for analysis
- 🔒 **Secure & Private** - Documents are processed securely and never permanently stored
- 🌓 **Dark/Light Mode** - Full theme support with persistent user preferences
- ⚡ **Real-time Progress** - Live processing updates with animated progress indicators
- 📥 **Data Export** - Export results as JSON or CSV formats

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Runtime**: React 19.2
- **Styling**: Tailwind CSS 4 with oklch color system
- **Animations**: Framer Motion
- **Data Visualization**: Recharts
- **UI Components**: shadcn/ui
- **Theme Management**: next-themes
- **Icons**: Lucide React
- **Language**: TypeScript

## Project Structure

```
app/
├── layout.tsx              # Root layout with theme provider
├── page.tsx               # Home page with hero and features
├── not-found.tsx          # 404 page
├── layout-wrapper.tsx     # Page transition wrapper
├── upload/
│   └── page.tsx          # PDF upload page
├── progress/
│   └── page.tsx          # Processing progress page
├── results/
│   └── page.tsx          # Results and data visualization
└── globals.css           # Global styles and design tokens

components/
├── header.tsx            # Navigation header with theme toggle
├── footer.tsx            # Footer with links
├── page-container.tsx    # Layout wrapper for consistent spacing
├── feature-card.tsx      # Reusable feature card component
├── file-upload-zone.tsx  # Drag-and-drop file upload
├── progress-display.tsx  # Progress bar with status
├── data-visualization.tsx # Chart component wrapper
├── export-buttons.tsx    # Export to JSON/CSV buttons
├── scroll-to-top.tsx     # Scroll to top button
└── ui/                   # shadcn/ui components
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- pnpm (recommended) or npm

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mat-extract-ai
```

2. Install dependencies:
```bash
pnpm install
```

3. Run the development server:
```bash
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Key Features Explained

### Dark/Light Mode
The app uses `next-themes` for persistent theme management. Theme preference is stored in localStorage and applied across all pages.

### Animations
Framer Motion is used throughout for:
- Page transitions
- Progress bar animations
- Button hover effects
- Data entry animations
- Scroll-triggered animations

### Design System
- **Colors**: Professional dark theme with blue/purple accents using oklch color space
- **Spacing**: Consistent spacing scale using Tailwind utilities
- **Typography**: Geist font family for all text
- **Responsive**: Mobile-first design with breakpoints at sm, md, lg, xl

### Components

#### Header
- Responsive navigation with mobile menu
- Theme toggle button
- Logo linking to home

#### FileUploadZone
- Drag-and-drop file upload
- File validation (PDF only, max 50MB)
- Visual feedback for drag states
- File information display

#### ProgressDisplay
- Animated progress bar
- Status indicators (idle, processing, complete)
- Current step display
- Time remaining estimation

#### DataVisualization
- Bar and line charts using Recharts
- Responsive sizing
- Custom theming to match app colors

#### ExportButtons
- Copy to clipboard functionality
- JSON export
- CSV export with proper formatting

## Design Tokens

The app uses semantic design tokens defined in `globals.css`:

- `--background` / `--foreground`: Base colors
- `--primary` / `--accent`: Brand colors
- `--card`: Card backgrounds
- `--border`: Border colors
- `--destructive`: Error states

All tokens have light and dark mode variants.

## Performance Optimizations

- Component code splitting
- Image optimization with Next.js Image
- CSS-in-JS with Tailwind JIT compilation
- Responsive images and lazy loading
- Framer Motion with GPU acceleration

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive components
- Keyboard navigation support
- High contrast ratios for readability
- Screen reader friendly

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Deployment

### Deploy to Vercel

1. Push to GitHub
2. Import in Vercel Dashboard
3. Vercel automatically detects Next.js configuration
4. Deploy with one click

```bash
vercel deploy
```

### Environment Variables

No environment variables required for the UI. Backend integration would require:
- API endpoints for PDF processing
- Authentication tokens
- Database credentials

## Future Enhancements

- [ ] User authentication and accounts
- [ ] PDF file history and management
- [ ] Advanced filtering and search
- [ ] Custom extraction templates
- [ ] Batch processing
- [ ] API for programmatic access
- [ ] Real backend integration
- [ ] Multi-language support

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact support@matextractai.com

---

Built with ❤️ using Next.js, React, and Tailwind CSS
