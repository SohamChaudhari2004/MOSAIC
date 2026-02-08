# 🎨 MOSAIC UI

Next.js 15 frontend for MOSAIC - Modern, responsive web interface for video analysis.

## 📋 Overview

The `mosaic-ui` is the web frontend that provides:
- Video upload interface with drag & drop
- Interactive chat with AI agent
- Real-time video search
- Video playback and clip viewing
- Responsive design for all devices
- Dark mode support (coming soon)

## 🏗️ Architecture

```
mosaic-ui/
├── app/
│   ├── page.tsx         # Home page
│   ├── layout.tsx       # Root layout
│   └── globals.css      # Global styles
├── components/
│   ├── ChatArea.tsx     # Chat interface
│   ├── Sidebar.tsx      # Video library sidebar
│   └── [others]/        # Reusable components
├── lib/
│   └── api.ts           # API client
├── public/              # Static assets
├── Dockerfile           # Docker build
├── next.config.ts       # Next.js configuration
└── package.json         # Dependencies
```

## 🔧 Technology Stack

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first CSS
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Lucide React** - Icon library

## 📦 Installation

### Using Docker (Recommended)

```bash
# From root directory
docker-compose up frontend

# Or build separately
cd mosaic-ui
docker build -t mosaic-ui .
docker run -p 3000:3000 mosaic-ui
```

### Local Development

```bash
cd mosaic-ui

# Install dependencies
npm install

# Set environment variable
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

## 🌐 Pages & Routes

### Home Page (`/`)

Main application interface with:
- Video upload area
- Chat interface
- Video library sidebar
- Search results display

### Future Routes (Planned)
- `/videos/:id` - Video detail page
- `/clips` - Generated clips library
- `/settings` - User settings
- `/help` - Documentation

## 🎨 Components

### ChatArea Component

Main chat interface for interacting with videos.

```tsx
<ChatArea
  videoId={currentVideoId}
  onSendMessage={handleMessage}
/>
```

**Features:**
- Message history display
- Typing indicator
- Auto-scroll to latest message
- Markdown support for responses
- Code syntax highlighting

### Sidebar Component

Video library and navigation.

```tsx
<Sidebar
  videos={videoList}
  onSelectVideo={handleSelectVideo}
  onUploadVideo={handleUpload}
/>
```

**Features:**
- Video thumbnail previews
- Upload progress indicator
- Video metadata display
- Search/filter videos
- Delete video option

### VideoPlayer (Coming Soon)

```tsx
<VideoPlayer
  videoId={videoId}
  startTime={120}
  autoPlay={true}
/>
```

### SearchResults (Coming Soon)

```tsx
<SearchResults
  results={results}
  onFrameClick={handleFrameClick}
/>
```

## 🔌 API Integration

### API Client (`lib/api.ts`)

```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload video
export const uploadVideo = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/videos/upload', formData);
};

// Send chat message
export const sendMessage = async (message: string, videoId: string) => {
  return api.post('/api/chat', { message, video_id: videoId });
};

// Search videos
export const searchVideo = async (query: string, videoId: string) => {
  return api.post('/api/search/combined', {
    query,
    video_id: videoId,
    top_k: 10,
  });
};
```

## 🎨 Styling

### TailwindCSS Configuration

```typescript
// tailwind.config.ts
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {...},
        secondary: {...},
      },
    },
  },
};
```

### Global Styles

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors;
  }
}
```

## 🚀 Features

### Video Upload

- **Drag & Drop**: Intuitive file upload
- **Progress Bar**: Real-time upload progress
- **File Validation**: Size and format checking
- **Multi-upload**: Queue multiple videos

### Chat Interface

- **Natural Language**: Ask questions in plain English
- **Contextual**: Agent remembers conversation history
- **Rich Responses**: Markdown formatting, code blocks
- **Streaming**: Real-time response streaming (planned)

### Video Library

- **Grid View**: Thumbnail previews
- **Metadata**: Duration, size, status
- **Search**: Filter by name or content
- **Management**: Delete, rename, share (planned)

### Search Results

- **Frame Thumbnails**: Visual results
- **Timestamps**: Jump to specific moments
- **Relevance Score**: Confidence indicators
- **Preview**: Hover for quick preview

## 📱 Responsive Design

```css
/* Mobile First Approach */
.container {
  @apply px-4;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    @apply px-6;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    @apply px-8 max-w-7xl mx-auto;
  }
}
```

## 🎭 Animations

### Framer Motion Examples

```tsx
import { motion } from 'framer-motion';

// Fade in animation
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.5 }}
>
  {children}
</motion.div>

// Slide in animation
<motion.div
  initial={{ x: -100, opacity: 0 }}
  animate={{ x: 0, opacity: 1 }}
  transition={{ type: 'spring', stiffness: 100 }}
>
  {children}
</motion.div>
```

## 🧪 Testing

```bash
# Run tests (when configured)
npm test

# Run tests in watch mode
npm run test:watch

# E2E tests with Playwright
npm run test:e2e
```

## 🔧 Configuration

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_TELEMETRY_DISABLED=1
```

### Next.js Config

```typescript
// next.config.ts
const nextConfig = {
  output: 'standalone', // For Docker
  images: {
    domains: ['localhost'],
  },
  experimental: {
    serverActions: true,
  },
};
```

## 🚀 Deployment

### Production Build

```bash
# Build production version
npm run build

# Start production server
npm start

# Or use Docker
docker build -t mosaic-ui .
docker run -p 3000:3000 mosaic-ui
```

### Environment Variables for Production

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

## 🎨 Customization

### Theme Colors

```typescript
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      brand: {
        50: '#f0f9ff',
        100: '#e0f2fe',
        // ... more shades
        900: '#0c4a6e',
      },
    },
  },
}
```

### Fonts

```typescript
// app/layout.tsx
import { Inter, Roboto_Mono } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });
const robotoMono = Roboto_Mono({ subsets: ['latin'] });
```

## 🐛 Debugging

### Enable Debug Mode

```bash
# Development mode with debugging
npm run dev -- --debug

# Check Next.js build
npm run build -- --debug
```

### React DevTools

Install the React DevTools browser extension for component inspection.

### Network Debugging

```typescript
// lib/api.ts
api.interceptors.request.use(request => {
  console.log('Starting Request', request);
  return request;
});

api.interceptors.response.use(response => {
  console.log('Response:', response);
  return response;
});
```

## 📈 Performance Optimization

### Image Optimization

```tsx
import Image from 'next/image';

<Image
  src="/video-thumbnail.jpg"
  alt="Video thumbnail"
  width={320}
  height={180}
  loading="lazy"
  placeholder="blur"
/>
```

### Code Splitting

```tsx
// Dynamic imports for heavy components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
  ssr: false,
});
```

### Memoization

```tsx
import { useMemo, useCallback } from 'react';

const MemoizedComponent = React.memo(({ data }) => {
  const processed = useMemo(() => processData(data), [data]);
  const handler = useCallback(() => handleEvent(), []);
  
  return <div>{processed}</div>;
});
```

## 🛠️ Development

### Code Quality

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint -- --fix

# Type check
npm run type-check
```

### Adding New Components

```bash
# Create component file
touch components/MyComponent.tsx

# Add to index
echo "export { default } from './MyComponent';" > components/MyComponent/index.ts
```

## 🤝 Contributing

1. Follow React best practices
2. Use TypeScript for type safety
3. Write accessible components (ARIA)
4. Add unit tests for complex logic
5. Document props with JSDoc

## 📞 Troubleshooting

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules
rm -rf node_modules
npm install
```

### API Connection Issues

```bash
# Check API URL
echo $NEXT_PUBLIC_API_URL

# Test API connection
curl http://localhost:8000/health
```

### Hot Reload Not Working

```bash
# Restart dev server
npm run dev

# Check file watchers limit (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Part of MOSAIC** - [Back to main project](../README.md)

## 🔗 Quick Links

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
