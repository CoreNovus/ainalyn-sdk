import React, { useEffect, useState } from "react";

export function PagefindSearch() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Pagefind assets 只在 build 後才存在
    // 需要考慮 basePath
    const script = document.createElement("script");
    script.src = "/docs/pagefind/pagefind-ui.js";
    script.async = true;
    script.onload = () => setReady(true);
    script.onerror = () => setReady(false);
    document.body.appendChild(script);

    // 載入 CSS
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/docs/pagefind/pagefind-ui.css";
    document.head.appendChild(link);
  }, []);

  const openSearch = () => {
    // @ts-ignore
    if (typeof window !== "undefined" && window.PagefindUI) {
      const modal = document.getElementById("pagefind-modal");
      if (modal) {
        modal.innerHTML = "";
        // @ts-ignore
        new window.PagefindUI({
          element: "#pagefind-modal",
          showSubResults: true,
          showImages: false
        });
        modal.classList.add("open");
        modal.style.display = "block";
      }
    }
  };

  if (!ready) {
    return null;
  }

  return (
    <>
      <button
        onClick={openSearch}
        style={{
          borderRadius: 8,
          padding: "6px 12px",
          border: "1px solid rgba(0,0,0,0.12)",
          backgroundColor: "transparent",
          cursor: "pointer",
          fontSize: 14
        }}
        title="Full-text search"
      >
        Search
      </button>
      <div
        id="pagefind-modal"
        style={{
          display: "none",
          position: "fixed",
          top: "10%",
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 1000,
          width: "90%",
          maxWidth: 600,
          backgroundColor: "white",
          borderRadius: 12,
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
          padding: 20
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            e.currentTarget.style.display = "none";
          }
        }}
      />
    </>
  );
}
