import { phaseTone } from "../tokens.js";

export function renderCountrySummaryCard(country, href) {
  return `
    <a class="country-gateway-card" href="${href}">
      <div class="country-gateway-head">
        <div>
          <p class="country-kicker">${country.country}</p>
          <h3>${country.handbook.country_label}</h3>
        </div>
        <span class="phase-badge ${phaseTone(country.decision.final_phase)}">${country.handbook.phase_label}</span>
      </div>
      <p class="country-gateway-reason">${country.decision.reasons?.[0] ?? ""}</p>
      <div class="country-gateway-meta">
        <span>資料月份 ${country.as_of}</span>
        <span>進入分析</span>
      </div>
    </a>
  `;
}

export function renderOverviewTicker(country) {
  return `
    <article class="overview-ticker">
      <div class="overview-ticker-head">
        <span class="overview-ticker-country">${country.handbook.country_label}</span>
        <span class="phase-badge ${phaseTone(country.decision.final_phase)}">${country.handbook.phase_label}</span>
      </div>
      <p class="overview-ticker-copy">${country.decision.reasons?.[0] ?? ""}</p>
      <p class="overview-ticker-meta">更新至 ${country.as_of}</p>
    </article>
  `;
}

export function renderLensFrameworkStrip(siteContent) {
  const authors = (siteContent.home?.authors ?? [])
    .map(
      (author) => `
        <article class="framework-card">
          <p class="framework-label">${author.school}</p>
          <h3>${author.title}</h3>
          <p>${author.note ?? author.book ?? ""}</p>
        </article>
      `,
    )
    .join("");

  return `
    <section class="lens-framework-strip">
      <div class="section-heading">
        <p class="eyebrow">Lens Frameworks</p>
        <h2>三個鏡頭，各自保留完整指標體系</h2>
        <p>首頁只負責導覽。完整指標表與轉段訊號，放在各國頁的 lens workspace 裡。</p>
      </div>
      <div class="framework-grid">${authors}</div>
    </section>
  `;
}

export function renderDataSourceList(siteContent) {
  const rows = (siteContent.home?.data_sources ?? [])
    .map((item) => `<li>${item}</li>`)
    .join("");

  return `
    <section class="terminal-source-panel">
      <div class="section-heading">
        <p class="eyebrow">Data Discipline</p>
        <h2>只顯示能對齊的真實月份</h2>
        <p>資料月份與頁面生成日分開標示，避免把生成時間誤認成經濟資料時間。</p>
      </div>
      <ul class="lens-reasons">${rows}</ul>
    </section>
  `;
}
