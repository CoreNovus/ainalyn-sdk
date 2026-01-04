# Ainalyn Documentation

This is the official documentation site for the Ainalyn SDK, built with [Nextra](https://nextra.site/).

## Deployment URL

- Production: <https://ainalyn.corenovus.com/docs>

## Development

### Prerequisites

- Node.js 20+
- npm

### Install

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Open [http://localhost:3000/docs](http://localhost:3000/docs) in your browser.

### Build

```bash
npm run build
npm run postbuild
```

The static site will be generated in the `out/` directory.

## Project Structure

```text
ainalyn-docs/
├── pages/
│   ├── _app.tsx
│   ├── _meta.json
│   ├── index.mdx
│   └── docs/
│       ├── _meta.json
│       ├── index.mdx
│       └── v1/
│           ├── _meta.json
│           ├── getting-started/
│           ├── concepts/
│           ├── guides/
│           └── api-reference/
├── components/
│   ├── VersionSwitcher.tsx
│   └── PagefindSearch.tsx
├── styles/
│   └── globals.css
├── public/
│   └── robots.txt
├── theme.config.tsx
├── next.config.mjs
├── package.json
└── tsconfig.json
```

## Deployment

### GitHub Pages (Recommended)

1. Push to `main` branch
2. GitHub Actions will automatically build and deploy

### Manual Deployment

1. Build the site: `npm run build && npm run postbuild`
2. Upload the `out/` directory to your hosting provider
3. Ensure the site is served from `/docs` path

## Configuration

### Base Path

The site is configured to be served from `/docs`:

```js
// next.config.mjs
export default withNextra({
  basePath: "/docs"
});
```

### Search

- **Nextra Search**: Built-in search functionality
- **Pagefind**: Full-text search (generated during build)

## Adding Content

### New Page

1. Create a new `.mdx` file in the appropriate directory
2. Update the corresponding `_meta.json` file

### New Version

1. Create a new version directory (e.g., `pages/docs/v2/`)
2. Copy content from previous version
3. Update `pages/docs/_meta.json`
4. Update `components/VersionSwitcher.tsx`

## License

See the main repository for license information.
