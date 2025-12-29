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
    link: "https://github.com/CoreNovus/ainalyn-sdk"
  },

  docsRepositoryBase: "https://github.com/CoreNovus/ainalyn-sdk/tree/main/ainalyn-docs",

  // 右上角 search：Nextra 內建搜尋
  search: {
    placeholder: "Search docs..."
  },

  // 額外加：Pagefind 全文搜尋 + 版本切換
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
    content: `© ${new Date().getFullYear()} Corenovus`
  },

  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="Ainalyn SDK Documentation" />
      <meta property="og:description" content="Build task-oriented agents with Python" />
    </>
  ),

  useNextSeoProps() {
    return {
      titleTemplate: "%s – Ainalyn Docs"
    };
  }
};

export default config;
