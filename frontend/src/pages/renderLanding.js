import {
  renderCountrySummaryCard,
  renderDataSourceList,
  renderLensFrameworkStrip,
  renderOverviewTicker,
} from "../domain/landing.js";
import { buildNav, buildStatus, siteLinks } from "./shared.js";

function buildLanding(payload, siteContent, config) {
  const links = siteLinks(config);
  const countryCards = payload.countries
    .map((country) => renderCountrySummaryCard(country, country.country === "TW" ? links.tw : links.us))
    .join("");
  const overview = payload.countries.map(renderOverviewTicker).join("");

  return `
    ${buildNav(config)}
    <main class="page">
      <section class="hero terminal-hero">
        <div class="terminal-hero-copy">
          <p class="eyebrow">Market Phase Detector</p>
          <h1>Market Regime Terminal</h1>
          <p class="subtitle">用規則驅動的週期判讀，集中查看台灣與美國目前的市場相位、資料月份與鏡頭差異。</p>
        </div>
        <div class="terminal-hero-side">
          <p class="hero-note">判讀方式</p>
          <p>${siteContent.home.method_notice.zh}</p>
        </div>
      </section>
      <section class="market-overview-strip">${overview}</section>
      ${buildStatus(payload)}
      <section class="country-gateway-section">
        <div class="section-heading">
          <p class="eyebrow">Country Gateways</p>
          <h2>台灣與美國分析入口</h2>
          <p>首頁先給網站級結論。深入分析時，請進入各國 workspace 查看完整指標表與轉段關鍵訊號。</p>
        </div>
        <div class="country-gateway-grid">${countryCards}</div>
      </section>
      ${renderLensFrameworkStrip(siteContent)}
      ${renderDataSourceList(siteContent)}
    </main>
  `;
}

export function renderLanding(payload, siteContent, config) {
  return buildLanding(payload, siteContent, config);
}
