import { nextPhase, phaseLabel, phaseTone } from "../tokens.js";
import { renderMetricTable } from "./country.js";

const CYCLE_SEQUENCE = ["Recovery", "Growth", "Boom", "Recession"];

export function renderPhaseBadge(phase, label, attrs = "") {
  return `<span class="phase-badge ${phaseTone(phase)}" ${attrs}>${label}</span>`;
}

function renderWarningBadge(warningLabel, warningLevel) {
  if (!warningLabel) return "";
  return `<span class="warning-badge warning-${warningLevel ?? "moderate"}">${warningLabel}</span>`;
}

export function renderTransitionDriverList(selectedRow) {
  const items = (selectedRow.metrics ?? [])
    .filter((metric) => (selectedRow.transition_keys ?? []).includes(metric.id))
    .map((metric) => `<li><strong>${metric.label}</strong> ${metric.display_value ?? metric.value}</li>`)
    .join("");

  return `
    <div class="transition-driver-block">
      <h3>Transition Drivers</h3>
      <ul class="lens-reasons transition-driver-list">${items || "<li>No transition drivers for the selected month.</li>"}</ul>
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

function renderWarningBlock(selectedRow) {
  if (!selectedRow.warning_state) {
    return "";
  }
  const warningLabel = selectedRow.warning_label ?? "轉弱警訊";
  const warningReasons = selectedRow.warning_reasons ?? [];
  return `
    <div class="lens-side-block warning-block warning-${selectedRow.warning_level ?? "moderate"}">
      <h3>${warningLabel}</h3>
      <ul class="lens-reasons">${warningReasons.length ? warningReasons.map((signal) => `<li>${signal}</li>`).join("") : "<li>Warning state active.</li>"}</ul>
    </div>
  `;
}

function renderSemanticLensRows(semanticRows) {
  if (!semanticRows?.length) {
    return "";
  }

  const items = semanticRows
    .map((row) => {
      const transitionChip = row.is_transition_driver ? `<span class="transition-key-chip">轉段關鍵</span>` : "";
      const sourceChip = `<span class="source-type-chip source-type-${row.source_type}">${row.source_type}</span>`;
      const currentValues = (row.current_values ?? [])
        .map((value) => `<li><strong>${value.label}</strong> ${value.display_value}</li>`)
        .join("");
      return `
        <div class="semantic-row-card">
          <div class="semantic-row-head">
            ${transitionChip}
            ${sourceChip}
            <strong>${row.master_category}</strong>
          </div>
          <p class="semantic-row-description">${row.master_description}</p>
          <p class="semantic-row-site-map">${row.site_metric_label}</p>
          <ul class="lens-reasons semantic-row-values">${currentValues}</ul>
        </div>
      `;
    })
    .join("");

  return `
    <div class="lens-side-block semantic-row-block">
      <h3>Semantic Rows</h3>
      <div class="semantic-row-stack">${items}</div>
    </div>
  `;
}

export function renderTransposedMetricTable(transposed, selectedMonth) {
  const { metric_rows, semantic_rows, months, month_columns } = transposed;
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
            ${renderWarningBadge(column.warning_label, column.warning_level)}
          </button>
        </th>
      `,
    )
    .join("");

  const rows = (semantic_rows ?? []).length
    ? semantic_rows.map((row) => ({
        row_id: row.row_id,
        primary_label: row.master_category,
        secondary_label: row.site_metric_label,
        source_type: row.source_type,
        values: row.history_values ?? [],
        is_transition_driver: Boolean(row.is_transition_driver),
      }))
    : metric_rows.map((row) => ({
        row_id: row.metric_id,
        primary_label: row.label,
        secondary_label: "",
        source_type: "proxy",
        values: row.values,
        is_transition_driver: activeKeys.has(row.metric_id),
      }));

  const renderedRows = rows
    .map((row) => {
      const isTransitionKey = row.is_transition_driver;
      const rowClass = isTransitionKey ? "metric-row-transition-key transition-driver" : "";
      const cells = row.values
        .map((value) => {
          let statusCls = `cell-${value.status}`;
          if (isTransitionKey) statusCls += " cell-transition-key transition-driver";
          if (value.month === activeColumn.month) statusCls += " cell-selected";
          return `<td class="${statusCls}">${value.display_value}</td>`;
        })
        .join("");

      const transitionChip = isTransitionKey ? `<span class="transition-key-chip">轉段關鍵</span>` : "";
      const sourceChip = `<span class="source-type-chip source-type-${row.source_type}">${row.source_type}</span>`;
      const secondary = row.secondary_label ? `<small class="site-metric-subtitle">${row.secondary_label}</small>` : "";
      const label = `${transitionChip}${sourceChip}<span>${row.primary_label}</span>${secondary}`;
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
          <tbody>${renderedRows}</tbody>
        </table>
      </div>
      <div class="izaax-legend">
        <p>Only months with real phase transitions highlight the true transition-driving rows.</p>
        <p><span class="cell-positive">●</span> Positive <span class="cell-negative">●</span> Negative <span class="cell-neutral">●</span> Neutral</p>
      </div>
    </div>
  `;
}

export function renderLensDecisionPanel(bundle, selectedRow) {
  const cycleSummary = CYCLE_SEQUENCE.map((phase) => phaseLabel(phase)).join(" -> ");
  const modeLabels = {
    initial: "Initial",
    hold: "Hold",
    advance: "Advance",
    ambiguous_hold: "Ambiguous Hold",
    ambiguous_advance: "Ambiguous Advance",
  };
  const currentSignals = selectedRow.support_current_phase_signals ?? selectedRow.supporting_signals ?? [];
  const nextSignals = selectedRow.support_next_phase_signals ?? [];
  const conflictSignals = selectedRow.conflict_signals ?? selectedRow.conflicting_signals ?? [];
  const modeClass = String(selectedRow.decision_mode || "hold").replace(/_/g, "-");

  return `
    <div class="izaax-side-panel lens-decision-panel" data-role="izaax-fixed-panel">
      <div class="izaax-side-block">
        <p class="lens-kicker">Current Decision</p>
        <h3>${selectedRow.month}</h3>
        <div class="izaax-current-phase">
          <span class="phase-badge-large ${phaseTone(selectedRow.phase)}">${selectedRow.phase_label}</span>
          ${renderWarningBadge(selectedRow.warning_label, selectedRow.warning_level)}
          <span class="izaax-next-info">Cycle Position: <strong>${cycleSummary}</strong></span>
        </div>
      </div>
      <div class="izaax-side-block izaax-decision-block ${modeClass}">
        <h3>${modeLabels[selectedRow.decision_mode] ?? "Current Decision"}</h3>
        <p>${selectedRow.decision_summary || selectedRow.narrative || ""}</p>
        <p><strong>Current Stance:</strong> ${selectedRow.stance ?? "neutral"}</p>
      </div>
      ${renderWarningBlock(selectedRow)}
      ${renderTransitionDriverList(selectedRow)}
      ${renderSignalBlock("Support Current Phase", currentSignals, "No current-phase support signals.")}
      ${renderSignalBlock("Support Next Phase", nextSignals, "No next-phase support signals.")}
      ${renderSignalBlock("Conflict Signals", conflictSignals, "No conflict signals.")}
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
            <label class="slider-label" for="slider-${lensId}">月份滑桿</label>
            <input id="slider-${lensId}" class="lens-history-slider" type="range" min="0" max="${maxIndex}" value="${maxIndex}" step="1" />
          </div>
          <div data-role="history-table">${renderMetricTable(history, maxIndex)}</div>
        </div>
        <aside class="lens-side lens-decision-side">
          ${renderLensDecisionPanel(bundle, currentRow)}
          ${renderSemanticLensRows(currentRow.semantic_rows)}
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
