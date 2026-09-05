# Mosaic UI - Styling Guide

## Design System Overview

Modern, minimal UI with dark mode support, purple accent, and subtle grid background overlay.

## Color System (HSL CSS Variables)

### Light Mode

- **Primary**: `262 83% 58%` (Purple)
- **Background**: `0 0% 100%` (White)
- **Foreground**: `0 0% 10%` (Near black)
- **Card**: `0 0% 100%` with subtle border
- **Muted**: `0 0% 96%` (Light grey)
- **Border**: `0 0% 90%`

### Dark Mode

- **Primary**: `0 100% 50%` (Red accent)
- **Background**: `0 0% 0%` (Black)
- **Foreground**: `0 0% 85%` (Light grey)
- **Card**: `0 0% 5%` (Dark grey)
- **Muted**: `0 0% 15%`
- **Accent**: `0 80% 35%` (Dark red)

All colors accessible via `hsl(var(--{color}))` in Tailwind.

## Typography

**Fonts** (Google Fonts via Next.js):

- **Display** (Headings): Space Grotesk - weights: 300, 400, 500, 600, 700
- **Body** (Text): Inter - weights: 300, 400, 500, 600

```tsx
// Applied in layout.tsx
className={`${spaceGrotesk.variable} ${inter.variable} antialiased`}
```

**Font Classes**:

- `font-display` - Headers (h1, h2)
- `font-body` - Body text

## Key Visual Elements

### Background Grid Overlay

Subtle 24x24px grid pattern on body:

- Light mode: `rgba(128, 128, 128, 0.03)` grey
- Dark mode: `rgba(255, 0, 0, 0.03)` red tint

### Border Radius

- `lg`: `0.5rem` (8px)
- `md`: `calc(0.5rem - 2px)` (6px)
- `sm`: `calc(0.5rem - 4px)` (4px)

### Custom Scrollbar

- Width: `8px`
- Thumb: `hsl(var(--muted-foreground) / 0.3)`
- Hover: `hsl(var(--muted-foreground) / 0.5)`

## Component Patterns

### Button Variants

```tsx
// Primary (default)
bg-primary text-primary-foreground hover:bg-primary/90

// Sizes: sm (h-9), default (h-10), lg (h-11), icon (10x10)
```

### Card Structure

```tsx
<Card> // rounded-lg border shadow-sm
  <CardHeader> // p-6
    <CardTitle> // text-2xl font-semibold
    <CardDescription> // text-sm muted
  <CardContent> // p-6 pt-0
  <CardFooter> // flex items-center p-6 pt-0
```

### Navigation

- Sticky header: `sticky top-0 z-50`
- Semi-transparent: `bg-black/80 backdrop-blur`
- Height: `h-16`
- Logo: Primary colored Video icon + "MOSAIC" text

## Theming

**Implementation**: `next-themes` provider

```tsx
<ThemeProvider>{children}</ThemeProvider>
```

**Toggle**: Class-based dark mode (`darkMode: "class"` in Tailwind)

## Utility Patterns

### Class Variance Authority (CVA)

Used for variant-based component styling (see Button component)

### CN Utility

Merge Tailwind classes with conflict resolution:

```tsx
import { cn } from "@/lib/utils"
className={cn("base-classes", conditionalClasses, className)}
```

## Animation

**Bounce** (used for loading states):

```css
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-25%);
  }
}
```

- With delays: `.delay-100`, `.delay-200`

## Best Practices

1. **Consistent spacing**: Use Tailwind spacing scale (p-4, p-6, gap-4, gap-6)
2. **Typography hierarchy**: Display font for headers, Body font for content
3. **Color usage**: Use CSS variables, never hard-coded colors
4. **Dark mode**: Test all components in both themes
5. **Hover states**: Always include hover transitions on interactive elements
6. **Focus rings**: `focus-visible:ring-2 focus-visible:ring-ring`
7. **Disabled states**: `disabled:opacity-50 disabled:pointer-events-none`

## File Structure

- `app/globals.css` - Global styles, CSS variables, animations
- `tailwind.config.ts` - Theme configuration, color mapping
- `components/ui/` - Reusable styled components
- `lib/utils.ts` - CN utility function
