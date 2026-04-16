import {
  renderCountryStatusBand,
  renderMetricTable,
  renderObservationChip,
  renderSitePhasePanel,
} from "../domain/country.js";
import {
  renderIzaaxLensRow,
  renderLensDecisionPanel,
  renderStandardLensRow,
  renderTransposedMetricTable,
} from "../domain/lens.js";
import { phaseTone } from "../tokens.js";
import { buildNav } from "./shared.js";

function buildCountryShell(country, config) {
  const observations = Object.entries(country.observations ?? {})
    .map(([key, value]) => renderObservationChip(key, value))
    .join("");

  return `
    ${buildNav(config)}
    <main class="page">
      ${renderCountryStatusBand(country)}
      <section class="hero hero-country country-command-header">
        <div class="hero-copy command-header-copy">
          <p class="eyebrow">國別策略地圖</p>
          <h1>${country.handbook.country_label}</h1>
          <p class="subtitle">每個 lens 都列出該作者完整會看的指標。切換月份後，會高亮正在推動下一階段或已造成轉段的訊號。</p>
        </div>
        ${renderSitePhasePanel(country)}
      </section>
      <section class="current-observation-strip country-terminal-stats">${observations}</section>
      <section id="lens-row-stack" class="lens-row-stack lens-workspace-stack"></section>
    </main>
  `;
}

function buildLensRow(lensId, bundle, strategyBook) {
  const history = bundle.history ?? [];
  const maxIndex = Math.max(history.length - 1, 0);
  const currentRow = history[maxIndex] ?? {
    month: "無資料",
    as_of: bundle.as_of ?? "",
    phase: bundle.phase,
    phase_label: bundle.phase_label,
    metrics: bundle.metrics ?? [],
    reasons: bundle.reasons ?? [],
  };

  if (lensId === "izaax" && bundle.transposed) {
    const selectedRow = history[maxIndex] ?? currentRow;
    return renderIzaaxLensRow(lensId, bundle, strategyBook, selectedRow);
  }

  return renderStandardLensRow(lensId, bundle, strategyBook, currentRow, maxIndex, history);
}

function createLensController(panel, lensId, bundle, strategyBook) {
  const independentSliderState = { index: Math.max((bundle.history ?? []).length - 1, 0) };
  const history = bundle.history ?? [];
  const slider = panel.querySelector(".lens-history-slider");

  if (lensId === "izaax") {
    const sidePanel = panel.querySelector('[data-role="izaax-side-panel"]');
    const mainPanel = panel.querySelector(".lens-main");

    function updateIzaaxMonth(month) {
      const row = history.find((item) => item.month === month) ?? history[history.length - 1];
      if (!row) {
        return;
      }
      const scrollWrapper = mainPanel.querySelector(".izaax-table-scroll-wrapper");
      const preservedScrollLeft = scrollWrapper?.scrollLeft ?? 0;
      const preservedScrollTop = scrollWrapper?.scrollTop ?? 0;
      mainPanel.innerHTML = renderTransposedMetricTable(bundle.transposed, row.month);
      sidePanel.innerHTML = renderLensDecisionPanel(bundle, row);
      const nextScrollWrapper = mainPanel.querySelector(".izaax-table-scroll-wrapper");
      if (nextScrollWrapper) {
        nextScrollWrapper.scrollLeft = preservedScrollLeft;
        nextScrollWrapper.scrollTop = preservedScrollTop;
      }
      mainPanel.querySelectorAll(".month-header-button").forEach((button) => {
        button.addEventListener("click", () => updateIzaaxMonth(button.dataset.month));
      });
    }

    updateIzaaxMonth(history[history.length - 1]?.month);
    return;
  }

  const badge = panel.querySelector('[data-role="phase-badge"]');
  const historyState = panel.querySelector('[data-role="history-state"]');
  const tableSlot = panel.querySelector('[data-role="history-table"]');
  const reasons = panel.querySelector('[data-role="reasons"]');
  const definition = panel.querySelector('[data-role="definition"]');
  const indicators = panel.querySelector('[data-role="indicators"]');
  const strategy = panel.querySelector('[data-role="strategy"]');

  function updateLensRow(nextIndex) {
    independentSliderState.index = Number(nextIndex);
    const row = history[independentSliderState.index] ?? history[history.length - 1];
    if (!row) {
      return;
    }
    const historyTableWrap = tableSlot.querySelector(".history-table-wrap");
    const preservedTableScrollLeft = historyTableWrap?.scrollLeft ?? 0;
    const preservedTableScrollTop = historyTableWrap?.scrollTop ?? 0;
    badge.textContent = row.phase_label;
    badge.className = `phase-badge ${phaseTone(row.phase)}`;
    historyState.textContent = `${row.month} ｜ 資料日 ${row.as_of}`;
    tableSlot.innerHTML = renderMetricTable(history, independentSliderState.index);
    const nextHistoryTableWrap = tableSlot.querySelector(".history-table-wrap");
    if (nextHistoryTableWrap) {
      nextHistoryTableWrap.scrollLeft = preservedTableScrollLeft;
      nextHistoryTableWrap.scrollTop = preservedTableScrollTop;
    }
    reasons.innerHTML = row.reasons.map((reason) => `<li>${reason}</li>`).join("");
    definition.textContent = strategyBook.phases?.[row.phase]?.definition ?? "";
    indicators.textContent = strategyBook.phases?.[row.phase]?.indicators ?? "";
    strategy.textContent = strategyBook.phases?.[row.phase]?.strategy ?? "";
  }

  slider.addEventListener("input", (event) => {
    updateLensRow(event.target.value);
  });
}

export function renderCountryPage(payload, siteContent, config) {
  const country = payload.countries.find((entry) => entry.country === config.country);
  if (!country) {
    throw new Error(`找不到 ${config.country} 的國別資料。`);
  }

  const app = document.getElementById("app");
  app.innerHTML = buildCountryShell(country, config);
  const container = document.getElementById("lens-row-stack");
  container.innerHTML = Object.entries(country.lenses ?? {})
    .map(([lensId, bundle]) => buildLensRow(lensId, bundle, siteContent.authors[lensId]))
    .join("");

  Object.entries(country.lenses ?? {}).forEach(([lensId, bundle]) => {
    const panel = container.querySelector(`[data-lens-id="${lensId}"]`);
    createLensController(panel, lensId, bundle, siteContent.authors[lensId]);
  });
}
