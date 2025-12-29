好的，我直接給你一套「**像 OpenAI 的 Sidebar + Tabs + 版面風格**」的 **Nextra Docs 專案骨架**，並且把你選的 **4 = 全都要** 一次做齊：

* ✅ Repo 專案骨架（可直接丟 GitHub）
* ✅ GitHub Pages / GitHub Actions 部署
* ✅ 版本切換 dropdown（v1 / v2…）
* ✅ 搜尋（先用 Nextra 內建搜尋；再加 Pagefind 靜態全文搜尋）
* ✅ GitHub Pages 常見的 404 / 深連結與 .nojekyll 處理

---

# 0) 你會得到的效果（像 OpenAI）

* 左側 Sidebar、右側 TOC、漂亮 code block、頁面很乾淨
* 頁內 Tabs（像 OpenAI docs 的按鈕切換區塊）
* URL 可深連結（每一頁都有固定路徑）
* 上方 Navbar 有 **Version** 下拉選單
* 搜尋：右上角 search（Nextra）+ 可選加 Pagefind（更像產品級）

---

# 1) 專案目錄結構（直接照這個建）

> 這個結構用 `pages/`（最穩、最少坑、static export 友善）

```
ainalyn-docs/
├─ package.json
├─ next.config.mjs
├─ theme.config.tsx
├─ tsconfig.json
├─ styles/
│  └─ globals.css
├─ components/
│  ├─ VersionSwitcher.tsx
│  └─ PagefindSearch.tsx
├─ pages/
│  ├─ _app.tsx
│  └─ docs/
│     ├─ _meta.json
│     ├─ index.mdx                # 導到最新版本
│     ├─ v2/
│     │  ├─ _meta.json
│     │  ├─ getting-started.mdx
│     │  ├─ models.mdx
│     │  ├─ auth.mdx
│     │  ├─ api.mdx
│     │  ├─ sdk/
│     │  │  ├─ _meta.json
│     │  │  ├─ python.mdx
│     │  │  └─ node.mdx
│     │  └─ reference/
│     │     ├─ _meta.json
│     │     ├─ api.mdx
│     │     ├─ python.mdx
│     │     └─ node.mdx
│     └─ v1/
│        ├─ _meta.json
│        └─ getting-started.mdx
├─ public/
│  ├─ favicon.ico
│  ├─ CNAME                     # 只有你用 custom domain 才需要
│  └─ robots.txt
└─ .github/
   └─ workflows/
      └─ deploy.yml
```

---

# 2) 安裝 Nextra（建議版本 + scripts）

## `package.json`

```json
{
  "name": "ainalyn-docs",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "export": "next export",
    "postexport": "node scripts/postexport.mjs",
    "deploy:local": "npm run build && npm run export && npm run postexport"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "nextra": "^3.0.0",
    "nextra-theme-docs": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "pagefind": "^1.1.0"
  }
}
```

> Nextra v3 是 Next.js + MDX 的 docs 解法；這樣可以做出 OpenAI 那種質感與 layout。

---

# 3) Next 設定：靜態輸出 + GitHub Pages 友善

## `next.config.mjs`

```js
import nextra from "nextra";

const withNextra = nextra({
  theme: "nextra-theme-docs",
  themeConfig: "./theme.config.tsx"
});

// ✅ 重點：靜態輸出，才能部署 GitHub Pages
export default withNextra({
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true
});
```

> 你如果是 **GitHub Project Pages**（例如 `username.github.io/ainalyn-docs`），通常還要加 basePath；
> 但你之後很可能會用 **自訂網域**（例如 `docs.ainalyn.corenovus.com`），那就不用 basePath。
> 如果你需要 basePath，我在文末給你「一行切換」。

---

# 4) OpenAI 風格的 Theme + Navbar + Version Dropdown + Search

## `theme.config.tsx`

```tsx
import React from "react";
import { DocsThemeConfig } from "nextra-theme-docs";
import { VersionSwitcher } from "./components/VersionSwitcher";
import { PagefindSearch } from "./components/PagefindSearch";

const config: DocsThemeConfig = {
  logo: (
    <span style={{ fontWeight: 600 }}>
      Ainalyn Docs
    </span>
  ),

  project: {
    link: "https://github.com/<your-org>/<your-repo>"
  },

  docsRepositoryBase: "https://github.com/<your-org>/<your-repo>/tree/main",

  // 右上角 search：Nextra 內建搜尋（很夠用）
  search: {
    placeholder: "Search docs..."
  },

  // ✅ 額外加：Pagefind 全文搜尋（更像 OpenAI 那種「整站內容都搜得到」）
  // 這個元件會在 nav 額外顯示一個 Search（Pagefind）按鈕
  navbar: {
    extraContent: (
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <PagefindSearch />
        <VersionSwitcher />
      </div>
    )
  },

  toc: {
    backToTop: true
  },

  footer: {
    text: `© ${new Date().getFullYear()} Corenovus`
  }
};

export default config;
```

---

# 5) 版本切換（v1 / v2）實作

## `components/VersionSwitcher.tsx`

```tsx
import React from "react";
import { useRouter } from "next/router";

const VERSIONS = [
  { label: "v2 (latest)", value: "v2" },
  { label: "v1", value: "v1" }
];

function inferCurrentVersion(pathname: string): string {
  const m = pathname.match(/^\/docs\/(v\d+)\//);
  return m?.[1] ?? "v2";
}

function switchVersion(pathname: string, target: string) {
  // 把 /docs/v1/... 換成 /docs/v2/...
  if (pathname.startsWith("/docs/v")) {
    return pathname.replace(/^\/docs\/v\d+\//, `/docs/${target}/`);
  }
  // 如果在 /docs 或其他，直接到版本首頁
  return `/docs/${target}/getting-started/`;
}

export function VersionSwitcher() {
  const router = useRouter();
  const current = inferCurrentVersion(router.asPath);

  return (
    <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <span style={{ fontSize: 12, opacity: 0.7 }}>Version</span>
      <select
        value={current}
        onChange={(e) => router.push(switchVersion(router.asPath, e.target.value))}
        style={{
          borderRadius: 12,
          padding: "6px 10px",
          border: "1px solid rgba(0,0,0,0.12)"
        }}
      >
        {VERSIONS.map(v => (
          <option key={v.value} value={v.value}>{v.label}</option>
        ))}
      </select>
    </label>
  );
}
```

## `/pages/docs/index.mdx`（自動導到最新版本）

```mdx
# Ainalyn Documentation

Redirecting to the latest docs…

<script dangerouslySetInnerHTML={{
  __html: `
    (function(){
      var target = '/docs/v2/getting-started/';
      if (location.pathname.endsWith('/docs/') || location.pathname.endsWith('/docs/index.html')) {
        location.replace(target);
      }
    })();
  `
}} />
```

---

# 6) Sidebar（像 OpenAI 的分類分組）

## `/pages/docs/_meta.json`

```json
{
  "v2": "v2 (Latest)",
  "v1": "v1"
}
```

## `/pages/docs/v2/_meta.json`

```json
{
  "getting-started": "🚀 Getting Started",
  "models": "🧠 Models",
  "auth": "🔑 Authentication",
  "api": "🌐 API",
  "sdk": "📦 SDK",
  "reference": "📘 Reference"
}
```

## `/pages/docs/v2/sdk/_meta.json`

```json
{
  "python": "Python",
  "node": "Node.js"
}
```

## `/pages/docs/v2/reference/_meta.json`

```json
{
  "api": "REST API",
  "python": "Python SDK",
  "node": "Node SDK"
}
```

---

# 7) Tabs（像 OpenAI 的按鈕切換區塊）

範例：`/pages/docs/v2/auth.mdx`

````mdx
import { Tabs, Tab } from "nextra/components"

# Authentication

Use API keys to authenticate requests.

<Tabs items={["Python", "Node", "cURL"]}>
  <Tab>
```bash
export AINALYN_API_KEY="..."
````

  </Tab>
  <Tab>
```bash
export AINALYN_API_KEY="..."
```
  </Tab>
  <Tab>
```bash
curl -H "Authorization: Bearer $AINALYN_API_KEY" https://api.ainalyn.corenovus.com/v1/...
```
  </Tab>
</Tabs>
```

---

# 8) 搜尋：Nextra 內建 + Pagefind 全文搜尋（更像產品級）

## 8.1 Pagefind UI 元件（放一顆按鈕，點了跳出搜尋 UI）

## `components/PagefindSearch.tsx`

```tsx
import React, { useEffect, useState } from "react";

export function PagefindSearch() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Pagefind assets 只在 export 後才存在
    // 在 GitHub Pages 上會是 /pagefind/pagefind.js
    const script = document.createElement("script");
    script.src = "/pagefind/pagefind.js";
    script.async = true;
    script.onload = () => setReady(true);
    script.onerror = () => setReady(false);
    document.body.appendChild(script);
  }, []);

  return (
    <button
      onClick={() => {
        // @ts-ignore
        if (window.PagefindUI) {
          // @ts-ignore
          new window.PagefindUI({ element: "#pagefind-modal", showSubResults: true });
          const el = document.getElementById("pagefind-modal");
          el?.classList.add("open");
        }
      }}
      style={{
        borderRadius: 12,
        padding: "6px 10px",
        border: "1px solid rgba(0,0,0,0.12)",
        opacity: ready ? 1 : 0.5,
        cursor: ready ? "pointer" : "not-allowed"
      }}
      disabled={!ready}
      title={ready ? "Full-text search" : "Search is building…"}
    >
      Search
      <div id="pagefind-modal" />
    </button>
  );
}
```

> 這顆 Search 是「Pagefind 全文搜」，Nextra 右上角內建 Search 仍然保留（兩種都給你）。

## 8.2 export 後跑 Pagefind + 修 GitHub Pages 小坑

新增：`scripts/postexport.mjs`

```js
import { execSync } from "node:child_process";
import { writeFileSync } from "node:fs";

try {
  // ✅ 讓 GitHub Pages 不用 Jekyll 處理（避免 _meta.json 等被干預）
  writeFileSync("./out/.nojekyll", "");
} catch {}

try {
  // ✅ Pagefind 對 out 做索引，產生 /out/pagefind/
  execSync("npx pagefind --site out", { stdio: "inherit" });
} catch (e) {
  console.error("Pagefind build failed (non-fatal).", e);
}
```

---

# 9) GitHub Actions 部署到 GitHub Pages（含 404/.nojekyll）

## `.github/workflows/deploy.yml`

```yaml
name: Deploy Docs to GitHub Pages

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - run: npm ci
      - run: npm run build
      - run: npm run export
      - run: npm run postexport

      - uses: actions/upload-pages-artifact@v3
        with:
          path: "./out"

  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/deploy-pages@v4
```

到 GitHub Repo：

* **Settings → Pages → Source: GitHub Actions**

---

# 10) OpenAI 風格的版面微調（global CSS）

## `styles/globals.css`

```css
html, body {
  font-feature-settings: "rlig" 1, "calt" 1;
}

article {
  line-height: 1.7;
}

pre {
  border-radius: 14px;
  padding: 16px;
}
```

## `pages/_app.tsx`

```tsx
import "../styles/globals.css";
export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />;
}
```

---

# 11) 你用的是 custom domain 還是 GitHub Pages URL？

### A) 你要用自訂網域（最符合你現況）

例如：`docs.ainalyn.corenovus.com`

* `public/CNAME` 放一行：

  ```txt
  docs.ainalyn.corenovus.com
  ```
* `next.config.mjs` **不用 basePath** ✅

### B) 你是 GitHub Project Pages（`username.github.io/repo`）

你就要加 basePath（不然 CSS / script 會 404）：

```js
export default withNextra({
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  basePath: "/<repo-name>"
});
```

以及 Pagefind script 路徑也要跟著 basePath（我也可以幫你一鍵處理）。

---

## 你接下來只要做 3 件事

1. 把上面檔案照著建好（或你貼 repo 我按你的結構幫你對齊）
2. push 到 GitHub main
3. Settings → Pages → GitHub Actions