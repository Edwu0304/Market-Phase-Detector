function getBodyConfig() {
  const body = document.body;
  return {
    page: body.dataset.page ?? "landing",
    country: body.dataset.country ?? null,
    root: body.dataset.root ?? ".",
  };
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`無法讀取 ${path}，狀態碼 ${response.status}`);
  }
  return response.json();
}

function siteLinks(config) {
  const rootPrefix = config.root === "." ? "." : "..";
  return {
    home: config.page === "landing" ? "./" : `${rootPrefix}/`,
    tw: config.page === "landing" ? "./tw/" : `${rootPrefix}/tw/`,
    us: config.page === "landing" ? "./us/" : `${rootPrefix}/us/`,
  };
}

function phaseTone(phase) {
  return `phase-${String(phase).toLowerCase()}`;
}

function phaseLabel(phase) {
  const labels = {
    Recovery: "復甦",
    Growth: "成長",
    Boom: "榮景",
    Recession: "衰退",
  };
  return labels[phase] ?? phase;
}

function formatDirection(value) {
  const labels = {
    improving: "改善",
    deteriorating: "惡化",
    stable: "持平",
    falling: "下降",
    rising: "上升",
    none: "無",
  };
  return labels[String(value)] ?? String(value);
}

function labelizeMetricKey(key) {
  const labels = {
    leading_index_change: "領先指標變動",
    claims_trend: "初領失業金方向",
    coincident_trend: "同時指標方向",
    coincident_direction_score: "同時指標方向分數",
    sahm_rule: "Sahm Rule",
    yield_curve: "10Y-2Y 殖利率差",
    hy_spread: "高收益債利差",
    business_signal_score: "景氣對策信號分數",
    leading_trend: "領先指標方向",
    unemployment_trend: "失業方向",
    exports_yoy: "出口年增率",
    as_of: "資料月份",
  };
  return labels[key] ?? key;
}

function formatScalar(value) {
  if (typeof value === "string") {
    return formatDirection(value);
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  return String(value);
}

function buildNav(config) {
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

function buildStatus(payload) {
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

function buildTheorySection(author) {
  const phaseBlocks = Object.entries(author.phases ?? {})
    .map(
      ([phase, content]) => `
        <article class="theory-phase-card ${phaseTone(phase)}">
          <div class="theory-phase-head">
            <span class="phase-badge ${phaseTone(phase)}">${phaseLabel(phase)}</span>
          </div>
          <dl class="theory-grid">
            <div>
              <dt>階段定義</dt>
              <dd>${content.definition}</dd>
            </div>
            <div>
              <dt>常見現象</dt>
              <dd>${content.phenomena}</dd>
            </div>
            <div>
              <dt>判斷指標</dt>
              <dd>${content.indicators}</dd>
            </div>
            <div>
              <dt>操作重點</dt>
              <dd>${content.strategy}</dd>
            </div>
          </dl>
        </article>
      `,
    )
    .join("");

  return `
    <section class="theory-section">
      <div class="section-heading">
        <p class="eyebrow">${author.school}</p>
        <h2>${author.title}</h2>
        <p>${author.book}</p>
      </div>
      <div class="theory-phase-stack">${phaseBlocks}</div>
    </section>
  `;
}

function buildDataSourceList(siteContent) {
  const rows = (siteContent.home?.data_sources ?? [])
    .map((item) => `<li>${item}</li>`)
    .join("");
  return `
    <section class="country-manuals">
      <div class="section-heading">
        <p class="eyebrow">資料原則</p>
        <h2>資料只採真實月份</h2>
        <p>網站只顯示台灣與美國都能對齊的真實月份，首頁生成日期不再混進歷史月份。</p>
      </div>
      <ul class="lens-reasons">${rows}</ul>
    </section>
  `;
}

function buildLanding(payload, siteContent, config) {
  const links = siteLinks(config);
  const countryCards = payload.countries
    .map((country) => `
      <a class="country-link-card" href="${country.country === "TW" ? links.tw : links.us}">
        <p class="country-kicker">${country.country} ${country.handbook.country_label}</p>
        <h3>${country.handbook.country_label}</h3>
        <p>首頁顯示的是網站總相位，不是任何一位大師的結論。</p>
        <p>${country.decision.reasons?.[0] ?? ""}</p>
        <div class="country-phase-row">
          <span class="phase-badge ${phaseTone(country.decision.final_phase)}">${country.handbook.phase_label}</span>
          <span>${country.as_of}</span>
        </div>
      </a>
    `)
    .join("");

  const theorySections = (siteContent.home?.authors ?? []).map(buildTheorySection).join("");

  return `
    ${buildNav(config)}
    <main class="page">
      <section class="hero hero-map">
        <div class="hero-copy">
          <p class="eyebrow">市場策略手冊</p>
          <h1>${siteContent.home.hero.title}</h1>
          <p class="subtitle">${siteContent.home.hero.subtitle}</p>
        </div>
        <div class="hero-panel">
          <p class="hero-note">判讀方式</p>
          <p>${siteContent.home.method_notice.zh}</p>
        </div>
      </section>
      ${buildStatus(payload)}
      <section class="country-manuals">
        <div class="section-heading">
          <p class="eyebrow">網站總相位</p>
          <h2>台灣與美國入口</h2>
          <p>這裡先給網站總相位，真正的三位大師獨立判讀，請進入各國頁查看三個橫向鏡頭、獨立時間軸與完整表格。</p>
        </div>
        <div class="country-grid">${countryCards}</div>
      </section>
      ${buildDataSourceList(siteContent)}
      ${theorySections}
    </main>
  `;
}

function buildCountryShell(country, config) {
  const observations = Object.entries(country.observations ?? {})
    .map(
      ([key, value]) => `
        <div class="observation-chip">
          <span>${labelizeMetricKey(key)}</span>
          <strong>${formatScalar(value)}</strong>
        </div>
      `,
    )
    .join("");

  return `
    ${buildNav(config)}
    <main class="page">
      <section class="hero hero-country">
        <div class="hero-copy">
          <p class="eyebrow">國別策略地圖</p>
          <h1>${country.handbook.country_label}</h1>
          <p class="subtitle">本頁上方先顯示網站總相位，下方三個鏡頭則分別代表三位作者的獨立判讀，不共用相位，也不共用時間軸。</p>
        </div>
        <aside class="hero-panel current-site-summary">
          <p class="hero-note">網站總相位</p>
          <div class="hero-phase ${phaseTone(country.decision.final_phase)}">${country.handbook.phase_label}</div>
          <p>資料月份：${country.as_of}</p>
          <p>${country.decision.reasons?.join(" ") ?? ""}</p>
        </aside>
      </section>
      <section class="current-observation-strip">${observations}</section>
      <section id="lens-row-stack" class="lens-row-stack"></section>
    </main>
  `;
}

function buildMetricTable(history, selectedIndex) {
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

// ===== Izaax Transposed Table =====
function buildIzaaxTransposedTable(transposed) {
  const {
    current_phase,
    current_phase_label,
    next_phase,
    prev_phase,
    phase_sequence,
    transition_keys,
    metric_rows,
    months,
    reasons,
  } = transposed;

  const currentIdx = phase_sequence.indexOf(current_phase);

  // Phase progression banner
  const phaseBanner = phase_sequence
    .map((ph, i) => {
      const label = { Recovery: "復甦", Growth: "成長", Boom: "榮景", Recession: "衰退" }[ph] || ph;
      const isActive = ph === current_phase;
      const isPrev = i === (currentIdx - 1 + phase_sequence.length) % phase_sequence.length;
      const isNext = i === (currentIdx + 1) % phase_sequence.length;
      let cls = "phase-step";
      if (isActive) cls += ` phase-step-active phase-${ph.toLowerCase()}`;
      else if (isPrev) cls += " phase-step-prev";
      else if (isNext) cls += " phase-step-next";
      const arrow = i < phase_sequence.length - 1 ? '<span class="phase-arrow">→</span>' : "";
      return `<span class="${cls}">${label}</span>${arrow}`;
    })
    .join("");

  // Month columns headers
  const monthHeaders = months.map((m) => `<th class="month-header">${m}</th>`).join("");

  // Metric rows with transition highlighting
  const metricRows = metric_rows
    .map((row) => {
      const isTransitionKey = row.is_transition_key;
      const rowClass = isTransitionKey ? "metric-row-transition-key" : "";
      const cells = row.values
        .map((v) => {
          let statusCls = `cell-${v.status}`;
          if (isTransitionKey) statusCls += " cell-transition-key";
          return `<td class="${statusCls}">${v.display_value}</td>`;
        })
        .join("");
      const labelPrefix = isTransitionKey ? '<span class="transition-key-indicator">★</span>' : "";
      return `<tr class="metric-row ${rowClass}"><th class="metric-label">${labelPrefix}${row.label}</th>${cells}</tr>`;
    })
    .join("");

  // Reasons
  const reasonsList = reasons.map((r) => `<li>${r}</li>`).join("");

  return `
    <div class="izaax-transposed">
      <div class="izaax-phase-banner">
        <div class="phase-progress">${phaseBanner}</div>
        <div class="izaax-current-phase">
          <span class="phase-badge-large ${phaseTone(current_phase)}">${current_phase_label}</span>
          <span class="izaax-next-info">下一步：<strong>${{ Recovery: "成長", Growth: "榮景", Boom: "衰退", Recession: "復甦" }[next_phase] || next_phase}</strong></span>
        </div>
      </div>
      <div class="izaax-table-scroll-wrapper">
        <table class="izaax-transposed-table">
          <thead>
            <tr>
              <th class="metric-col-header">指標</th>
              ${monthHeaders}
            </tr>
          </thead>
          <tbody>
            ${metricRows}
          </tbody>
        </table>
      </div>
      <div class="izaax-legend">
        <p><span class="transition-key-indicator">★</span> 表示影響進入下一階段的關鍵指標</p>
        <p><span class="cell-positive">●</span> 正向 <span class="cell-negative">●</span> 負向 <span class="cell-neutral">●</span> 中性</p>
      </div>
      <div class="izaax-reasons">
        <h3>判讀原因</h3>
        <ul>${reasonsList}</ul>
      </div>
    </div>
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

  // Izaax: full-width transposed table, no side panel, no slider
  if (lensId === "izaax" && bundle.transposed) {
    return `
      <article class="lens-row lens-row-izaax" data-lens-id="${lensId}">
        <div class="lens-row-head">
          <div>
            <p class="lens-kicker">${strategyBook.school}</p>
            <h2>${bundle.title}</h2>
            <p class="lens-book">${strategyBook.book}</p>
          </div>
        </div>
        <div class="lens-row-body lens-row-body-full">
          ${buildIzaaxTransposedTable(bundle.transposed)}
        </div>
      </article>
    `;
  }

  // Urakami / Marks: standard layout with slider + side panel
  return `
    <article class="lens-row" data-lens-id="${lensId}">
      <div class="lens-row-head">
        <div>
          <p class="lens-kicker">${strategyBook.school}</p>
          <h2>${bundle.title}</h2>
          <p class="lens-book">${strategyBook.book}</p>
        </div>
        <div class="lens-current">
          <span class="phase-badge ${phaseTone(currentRow.phase)}" data-role="phase-badge">${currentRow.phase_label}</span>
          <span class="history-state" data-role="history-state">${currentRow.month} ｜ 資料日 ${currentRow.as_of}</span>
        </div>
      </div>
      <div class="lens-row-body">
        <div class="lens-main">
          <div class="lens-history-toolbar">
            <label class="slider-label" for="slider-${lensId}">拉桿控制月份</label>
            <input id="slider-${lensId}" class="lens-history-slider" type="range" min="0" max="${maxIndex}" value="${maxIndex}" step="1" />
          </div>
          <div data-role="history-table">${buildMetricTable(history, maxIndex)}</div>
        </div>
        <aside class="lens-side">
          <div class="lens-side-block">
            <h3>當月判讀</h3>
            <ul class="lens-reasons" data-role="reasons">${currentRow.reasons.map((reason) => `<li>${reason}</li>`).join("")}</ul>
          </div>
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

function createLensController(panel, lensId, bundle, strategyBook) {
  const independentSliderState = { index: Math.max((bundle.history ?? []).length - 1, 0) };
  const history = bundle.history ?? [];
  const slider = panel.querySelector(".lens-history-slider");

  // Izaax uses transposed table, no slider control
  if (lensId === "izaax") {
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
    badge.textContent = row.phase_label;
    badge.className = `phase-badge ${phaseTone(row.phase)}`;
    historyState.textContent = `${row.month} ｜ 資料日 ${row.as_of}`;
    tableSlot.innerHTML = buildMetricTable(history, independentSliderState.index);
    reasons.innerHTML = row.reasons.map((reason) => `<li>${reason}</li>`).join("");
    definition.textContent = strategyBook.phases?.[row.phase]?.definition ?? "";
    indicators.textContent = strategyBook.phases?.[row.phase]?.indicators ?? "";
    strategy.textContent = strategyBook.phases?.[row.phase]?.strategy ?? "";
  }

  slider.addEventListener("input", (event) => {
    updateLensRow(event.target.value);
  });
}

function renderCountryPage(payload, siteContent, config) {
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

async function loadApplication() {
  const config = getBodyConfig();
  const payload = await fetchJson(`${config.root}/data/latest.json`);
  const siteContent = await fetchJson(`${config.root}/data/site-content.json`);
  const app = document.getElementById("app");

  if (config.page === "country") {
    renderCountryPage(payload, siteContent, config);
    return;
  }

  app.innerHTML = buildLanding(payload, siteContent, config);
}

loadApplication().catch((error) => {
  document.getElementById("app").innerHTML = `
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
});
