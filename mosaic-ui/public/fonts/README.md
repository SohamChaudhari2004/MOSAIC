# Font Setup

This project uses two custom fonts:

1. **Rhymes Display Light (400)** - for h1 and h2 headings
2. **Suisse Intl Book (400)** - for body text and other elements

## Installation

Place the following font files in the `public/fonts` directory:

- `RhymesDisplay-Light.woff2`
- `SuisseIntl-Book.woff2`

## Where to get the fonts

### Rhymes Display

- Available from: [Branding with Type](https://brandingwithtype.com/)
- Or use a similar display serif font as fallback

### Suisse Intl

- Available from: [Swiss Typefaces](https://www.swisstypefaces.com/)
- Or use a similar clean sans-serif font as fallback

## Fallback Fonts

If you don't have access to these commercial fonts, the configuration includes fallback fonts:

- Rhymes Display → generic serif
- Suisse Intl → generic sans-serif

The layout will still work beautifully with system fonts as fallbacks.

## Usage in Code

The fonts are configured in:

- `app/layout.tsx` - Font loading
- `tailwind.config.ts` - Font family variables
- `app/globals.css` - @font-face declarations

You can use them in your components with:

```tsx
<h1 className="font-display">Heading</h1>
<p className="font-body">Body text</p>
```
