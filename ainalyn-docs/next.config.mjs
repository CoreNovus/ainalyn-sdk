import nextra from "nextra";

const withNextra = nextra({
  theme: "nextra-theme-docs",
  themeConfig: "./theme.config.tsx"
});

// 部署到 ainalyn.corenovus.com/docs
export default withNextra({
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  basePath: "/docs"
});
