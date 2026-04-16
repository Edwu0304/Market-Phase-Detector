import { formatScalar } from "../formatters.js";
import { labelizeMetricKey, phaseTone } from "../tokens.js";

export function renderObservationChip(key, value) {
  return `
    <div class="observation-chip terminal-stat-tile">
      <span>${labelizeMetricKey(key)}</span>
      <strong>${formatScalar(value)}</strong>
    </div>
  `;
}

export function renderCountryStatusBand(country) {
  const watch = country.decision.watch
    ? `<span class="status-pill country-watch-pill">${country.decision.watch}</span>`
    : "";

  return `
    <section class="country-status-band">
      <div class="country-status-band-main">
        <span class="country-status-label">${country.handbook.country_label}</span>
        <span class="phase-badge ${phaseTone(country.decision.final_phase)}">${country.handbook.phase_label}</span>
        ${watch}
      </div>
      <div class="country-status-band-meta">
        <span>資料月份 ${country.as_of}</span>
        <span>Site Phase</span>
      </div>
    </section>
  `;
}

export function renderSitePhasePanel(country) {
  return `
    <aside class="current-site-summary command-summary-panel">
      <p class="hero-note">網站總相位</p>
      <div class="hero-phase ${phaseTone(country.decision.final_phase)}">${country.handbook.phase_label}</div>
      <p>資料月份：${country.as_of}</p>
      <p>${country.decision.reasons?.join(" ") ?? ""}</p>
    </aside>
  `;
}

export function renderMetricTable(history, selectedIndex) {
  const selectedRow = history[selectedIndex] ?? history[history.length - 1] ?? { metrics: [] };
  const headers = (selectedRow.metrics ?? []).map((metric) => `<th>${metric.label}</th>`).join("");
  const rows = history
    .map(
      (row, index) => `
        <tr class="${index === selectedIndex ? "is-selected" : ""}">
          <td>${row.month}</td>
          <td>${row.phase_label}</td>
          ${(row.metrics ?? []).map((metric) => `<td>${metric.display_value ?? metric.value}</td>`).join("")}
        </tr>
      `,
    )
    .join("");

  return `
    <div class="history-table-wrap">
      <table class="history-table">
        <thead>
          <tr>
            <th>月份</th>
            <th>相位</th>
            ${headers}
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}
