import React from "react";
import { useRouter } from "next/router";

const VERSIONS = [
  { label: "v1 (latest)", value: "v1" }
  // 未來可以加入更多版本
  // { label: "v2", value: "v2" },
];

function inferCurrentVersion(pathname: string): string {
  const m = pathname.match(/\/docs\/(v\d+)\//);
  return m?.[1] ?? "v1";
}

function switchVersion(pathname: string, target: string) {
  // 把 /docs/v1/... 換成 /docs/v2/...
  if (pathname.includes("/docs/v")) {
    return pathname.replace(/\/docs\/v\d+\//, `/docs/${target}/`);
  }
  // 如果在 /docs 或其他，直接到版本首頁
  return `/docs/${target}/getting-started/`;
}

export function VersionSwitcher() {
  const router = useRouter();
  const current = inferCurrentVersion(router.asPath);

  // 只有一個版本時，直接顯示版本標籤
  if (VERSIONS.length === 1) {
    return (
      <span
        style={{
          fontSize: 12,
          padding: "4px 8px",
          borderRadius: 8,
          backgroundColor: "rgba(0,0,0,0.05)",
          color: "inherit"
        }}
      >
        {VERSIONS[0].label}
      </span>
    );
  }

  return (
    <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <span style={{ fontSize: 12, opacity: 0.7 }}>Version</span>
      <select
        value={current}
        onChange={(e) => router.push(switchVersion(router.asPath, e.target.value))}
        style={{
          borderRadius: 12,
          padding: "6px 10px",
          border: "1px solid rgba(0,0,0,0.12)",
          backgroundColor: "transparent",
          cursor: "pointer"
        }}
      >
        {VERSIONS.map(v => (
          <option key={v.value} value={v.value}>{v.label}</option>
        ))}
      </select>
    </label>
  );
}
