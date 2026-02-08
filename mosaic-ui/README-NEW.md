# Mosaic UI - Modern Multi-Page Application

A beautiful, modern web application built with Next.js 16, TypeScript, and Tailwind CSS, featuring custom fonts and shadcn/ui components.

## Features

- 🎨 **Modern Design**: Clean, professional UI with custom typography
- 📱 **Responsive**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast**: Built with Next.js 16 for optimal performance
- 🎭 **Custom Fonts**: Uses Rhymes Display Light for headings and Suisse Intl Book for body text
- 🧩 **Component Library**: Built with shadcn/ui components
- 🎯 **Multiple Pages**: Landing, Features, Pricing, About, and App pages

## Pages

- **Landing Page** (`/landing`) - Beautiful hero section with features and CTA
- **App Page** (`/app`) - Main application interface with chat functionality
- **Features Page** (`/features`) - Detailed feature showcase
- **Pricing Page** (`/pricing`) - Pricing tiers and plans
- **About Page** (`/about`) - Company mission and values

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
```

2. Add custom fonts (optional):
   - Place `RhymesDisplay-Light.woff2` and `SuisseIntl-Book.woff2` in `public/fonts/`
   - See `public/fonts/README.md` for details

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
mosaic-ui/
├── app/
│   ├── landing/          # Landing page
│   ├── app/              # Main app interface
│   ├── features/         # Features page
│   ├── pricing/          # Pricing page
│   ├── about/            # About page
│   ├── layout.tsx        # Root layout with font setup
│   ├── page.tsx          # Home redirect
│   └── globals.css       # Global styles and theme
├── components/
│   ├── ui/               # shadcn/ui components
│   └── Navigation.tsx    # Main navigation component
├── lib/
│   ├── api.ts            # API client
│   └── utils.ts          # Utility functions
└── public/
    └── fonts/            # Custom font files
```

## Customization

### Fonts

The project uses:

- **Rhymes Display Light (400)** for h1 and h2
- **Suisse Intl Book (400)** for body text

To change fonts, edit:

- `app/layout.tsx` - Font loading
- `tailwind.config.ts` - Font family configuration
- `app/globals.css` - @font-face declarations

### Theme

Colors and theming are configured in:

- `app/globals.css` - CSS variables for light/dark mode
- `tailwind.config.ts` - Tailwind theme extensions

### Components

All UI components are in `components/ui/` and use the shadcn/ui pattern:

- Button
- Card
- Input
- Badge
- Container
- Section

## Tech Stack

- **Framework**: Next.js 16
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui
- **Icons**: Lucide React
- **Utilities**: clsx, tailwind-merge, class-variance-authority

## Building for Production

```bash
npm run build
npm start
```

## License

MIT
