import { nextPhase, phaseLabel, phaseTone } from "../tokens.js";
import { renderMetricTable } from "./country.js";

export function renderPhaseBadge(phase, label, attrs = "") {
  return `<span class="phase-badge ${phaseTone(phase)}" ${attrs}>${label}</span>`;
}

export function renderTransitionDriverList(selectedRow) {
  const items = (selectedRow.metrics ?? [])
    .filter((metric) => (selectedRow.transition_keys ?? []).includes(metric.id))
    .map((metric) => `<li><strong>${metric.label}</strong> ${metric.display_value ?? metric.value}</li>`)
    .join("");

  return `
    <div class="transition-driver-block">
      <h3>Transition Drivers</h3>
      <ul class="lens-reasons transition-driver-list">${items || "<li>本月沒有明確推動下一階段的核心指標。</li>"}</ul>
    </div>
  `;
}

function renderSignalBlock(title, signals, emptyText) {
  return `
    <div class="lens-side-block">
      <h3>${title}</h3>
      <ul class="lens-reasons">${signals.length ? signals.map((signal) => `<li>${signal}</li>`).join("") : `<li>${emptyText}</li>`}</ul>
    </div>
  `;
}

export function renderTransposedMetricTable(transposed, selectedMonth) {
  const { metric_rows, months, month_columns } = transposed;
  const columns = month_columns ?? months.map((month) => ({ month, phase: "", phase_label: "" }));
  const activeColumn =
    columns.find((column) => column.month === selectedMonth) ??
    columns[columns.length - 1] ??
    { transition_keys: [] };
  const activeKeys = new Set(activeColumn.transition_keys ?? []);

  const monthHeaders = columns
    .map(
      (column) => `
        <th class="month-header ${column.month === activeColumn.month ? "is-selected" : ""}">
          <button class="month-header-button" data-month="${column.month}">
            <span class="month-header-label">${column.month}</span>
            <span class="month-phase-badge ${phaseTone(column.phase)}">${column.phase_label ?? ""}</span>
          </button>
        </th>
      `,
    )
    .join("");

  const metricRows = metric_rows
    .map((row) => {
      const isTransitionKey = activeKeys.has(row.metric_id);
      const rowClass = isTransitionKey ? "metric-row-transition-key transition-driver" : "";
      const cells = row.values
        .map((value) => {
          let statusCls = `cell-${value.status}`;
          if (isTransitionKey) statusCls += " cell-transition-key transition-driver";
          if (value.month === activeColumn.month) statusCls += " cell-selected";
          return `<td class="${statusCls}">${value.display_value}</td>`;
        })
        .join("");
      const label = isTransitionKey
        ? `<span class="transition-key-chip">轉段關鍵</span><span>${row.label}</span>`
        : `<span>${row.label}</span>`;
      return `<tr class="metric-row ${rowClass}"><th class="metric-label">${label}</th>${cells}</tr>`;
    })
    .join("");

  return `
    <div class="izaax-transposed" data-role="izaax-table-pane">
      <div class="izaax-table-scroll-wrapper">
        <table class="izaax-transposed-table">
          <thead>
            <tr>
              <th class="metric-col-header">指標</th>
              ${monthHeaders}
            </tr>
          </thead>
          <tbody>${metricRows}</tbody>
        </table>
      </div>
      <div class="izaax-legend">
        <p>只有發生轉段或真正推動下一階段的指標會被高亮。</p>
        <p><span class="cell-positive">●</span> 正向 <span class="cell-negative">●</span> 負向 <span class="cell-neutral">●</span> 中性</p>
      </div>
    </div>
  `;
}

export function renderLensDecisionPanel(bundle, selectedRow) {
  const cycleSummary = `${phaseLabel(selectedRow.previous_phase ?? selectedRow.phase)} -> ${phaseLabel(selectedRow.phase)} -> ${phaseLabel(nextPhase(selectedRow.phase))}`;
  const modeLabels = {
    initial: "初始判定",
    hold: "維持現階段",
    advance: "前進一階",
    ambiguous_hold: "保守維持",
    ambiguous_advance: "保守前進",
  };
  const currentSignals = selectedRow.support_current_phase_signals ?? selectedRow.supporting_signals ?? [];
  const nextSignals = selectedRow.support_next_phase_signals ?? [];
  const conflictSignals = selectedRow.conflict_signals ?? selectedRow.conflicting_signals ?? [];
  const modeClass = String(selectedRow.decision_mode || "hold").replace(/_/g, "-");

  return `
    <div class="izaax-side-panel lens-decision-panel" data-role="izaax-fixed-panel">
      <div class="izaax-side-block">
        <p class="lens-kicker">當期判讀</p>
        <h3>${selectedRow.month}</h3>
        <div class="izaax-current-phase">
          <span class="phase-badge-large ${phaseTone(selectedRow.phase)}">${selectedRow.phase_label}</span>
          <span class="izaax-next-info">循環位置：<strong>${cycleSummary}</strong></span>
        </div>
      </div>
      <div class="izaax-side-block izaax-decision-block ${modeClass}">
        <h3>${modeLabels[selectedRow.decision_mode] ?? "當月判讀"}</h3>
        <p>${selectedRow.decision_summary || selectedRow.narrative || ""}</p>
        <p><strong>目前立場：</strong>${selectedRow.stance ?? "neutral"}</p>
      </div>
      ${renderTransitionDriverList(selectedRow)}
      ${renderSignalBlock("Support Current Phase", currentSignals, "本月沒有足夠訊號支撐當前階段。")}
      ${renderSignalBlock("Support Next Phase", nextSignals, "本月沒有足夠訊號支持下一階段。")}
      ${renderSignalBlock("Conflict Signals", conflictSignals, "本月沒有明顯衝突訊號。")}
      <div class="lens-side-block">
        <h3>Raw Evidence</h3>
        <ul class="lens-reasons">${(selectedRow.reasons ?? []).map((reason) => `<li>${reason}</li>`).join("")}</ul>
      </div>
    </div>
  `;
}

export function renderStandardLensRow(lensId, bundle, strategyBook, currentRow, maxIndex, history) {
  return `
    <article class="lens-row lens-workspace" data-lens-id="${lensId}">
      <div class="lens-row-head">
        <div class="lens-workspace-title">
          <p class="lens-kicker">${strategyBook.school}</p>
          <h2>${bundle.title}</h2>
          <p class="lens-book">${strategyBook.book}</p>
        </div>
        <div class="lens-current">
          ${renderPhaseBadge(currentRow.phase, currentRow.phase_label, 'data-role="phase-badge"')}
          <span class="history-state" data-role="history-state">${currentRow.month} ｜ 資料日 ${currentRow.as_of}</span>
        </div>
      </div>
      <div class="lens-row-body">
        <div class="lens-main">
          <div class="lens-history-toolbar">
            <label class="slider-label" for="slider-${lensId}">切換月份</label>
            <input id="slider-${lensId}" class="lens-history-slider" type="range" min="0" max="${maxIndex}" value="${maxIndex}" step="1" />
          </div>
          <div data-role="history-table">${renderMetricTable(history, maxIndex)}</div>
        </div>
        <aside class="lens-side lens-decision-side">
          ${renderLensDecisionPanel(bundle, currentRow)}
          <div class="lens-side-block">
            <h3>階段定義</h3>
            <p data-role="definition">${strategyBook.phases?.[currentRow.phase]?.definition ?? ""}</p>
          </div>
          <div class="lens-side-block">
            <h3>判斷指標</h3>
            <p data-role="indicators">${strategyBook.phases?.[currentRow.phase]?.indicators ?? ""}</p>
          </div>
          <div class="lens-side-block">
            <h3>操作重點</h3>
            <p data-role="strategy">${strategyBook.phases?.[currentRow.phase]?.strategy ?? ""}</p>
          </div>
        </aside>
      </div>
    </article>
  `;
}

export function renderIzaaxLensRow(lensId, bundle, strategyBook, selectedRow) {
  return `
    <article class="lens-row lens-row-izaax lens-workspace" data-lens-id="${lensId}">
      <div class="lens-row-head">
        <div class="lens-workspace-title">
          <p class="lens-kicker">${strategyBook.school}</p>
          <h2>${bundle.title}</h2>
          <p class="lens-book">${strategyBook.book}</p>
        </div>
      </div>
      <div class="lens-row-body lens-row-body-izaax">
        <div class="lens-main izaax-main-pane">
          ${renderTransposedMetricTable(bundle.transposed, selectedRow.month)}
        </div>
        <aside class="lens-side izaax-side-pane" data-role="izaax-side-panel">
          ${renderLensDecisionPanel(bundle, selectedRow)}
        </aside>
      </div>
    </article>
  `;
}
