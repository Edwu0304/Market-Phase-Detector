export function siteLinks(config) {
  const rootPrefix = config.root === "." ? "." : "..";
  return {
    home: config.page === "landing" ? "./" : `${rootPrefix}/`,
    tw: config.page === "landing" ? "./tw/" : `${rootPrefix}/tw/`,
    us: config.page === "landing" ? "./us/" : `${rootPrefix}/us/`,
  };
}

export function buildNav(config) {
  const links = siteLinks(config);
  return `
    <nav class="top-nav">
      <a class="brand" href="${links.home}">市場週期偵測器</a>
      <div class="nav-links">
        <a href="${links.home}">首頁</a>
        <a href="${links.tw}">台灣</a>
        <a href="${links.us}">美國</a>
      </div>
    </nav>
  `;
}

export function buildStatus(payload) {
  const error = payload.meta?.error
    ? `<span class="status-pill status-error">資料警示：${payload.meta.error}</span>`
    : "";
  return `
    <section class="status-bar">
      <span class="status-pill">資料來源：${payload.meta?.source ?? "未知"}</span>
      <span class="status-pill">頁面生成日：${payload.generated_at}</span>
      ${error}
    </section>
  `;
}

export function renderFatalLoadError(error) {
  return `
    <main class="page">
      <section class="hero">
        <div class="hero-copy">
          <p class="eyebrow">載入失敗</p>
          <h1>目前無法顯示頁面</h1>
          <p class="subtitle">${error.message}</p>
        </div>
      </section>
    </main>
  `;
}
