import { execSync } from "node:child_process";
import { writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const outDir = "./out";

try {
  // 確保 out 目錄存在
  if (!existsSync(outDir)) {
    console.log("Output directory not found, skipping postbuild...");
    process.exit(0);
  }

  // 讓 GitHub Pages 不用 Jekyll 處理（避免 _meta.json 等被干預）
  writeFileSync(join(outDir, ".nojekyll"), "");
  console.log("Created .nojekyll file");

  // Pagefind 對 out 做索引，產生 /out/pagefind/
  console.log("Running Pagefind indexing...");
  execSync("npx pagefind --site out", { stdio: "inherit" });
  console.log("Pagefind indexing complete!");

} catch (e) {
  console.error("Postbuild script encountered an error:", e.message);
  // 非致命錯誤，繼續
}
