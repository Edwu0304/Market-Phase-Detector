function getBodyConfig() {
  const body = document.body;
  return {
    page: body.dataset.page ?? "landing",
    country: body.dataset.country ?? null,
    root: body.dataset.root ?? ".",
  };
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.status}`);
  }
  return response.json();
}

function formatValue(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  return String(value);
}

function labelize(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function siteLinks(config) {
  const rootPrefix = config.root === "." ? "." : "..";
  return {
    home: config.page === "landing" ? "./" : `${rootPrefix}/`,
    tw: config.page === "landing" ? "./tw/" : `${rootPrefix}/tw/`,
    us: config.page === "landing" ? "./us/" : `${rootPrefix}/us/`,
  };
}

function buildNav(config) {
  const links = siteLinks(config);
  return `
    <nav class="top-nav">
      <a class="brand" href="${links.home}">Market Phase Detector</a>
      <div class="nav-links">
        <a href="${links.home}">Cycle Map</a>
        <a href="${links.tw}">Taiwan</a>
        <a href="${links.us}">United States</a>
      </div>
    </nav>
  `;
}

function buildStatus(payload) {
  const source = payload.meta?.source ?? "unknown";
  const error = payload.meta?.error
    ? `<span class="status-pill status-error">Fallback: ${payload.meta.error}</span>`
    : "";

  return `
    <section class="status-bar">
      <span class="status-pill">Source: ${source}</span>
      <span class="status-pill">Generated: ${payload.generated_at}</span>
      ${error}
    </section>
  `;
}

function buildPhaseRail(phases, activePhase) {
  return `
    <section class="phase-rail">
      ${phases
        .map(
          (phase) => `
            <div class="phase-stop ${phase.phase === activePhase ? "is-active" : ""}">
              <span class="phase-stop-label">${phase.label}</span>
            </div>
          `,
        )
        .join("")}
    </section>
  `;
}

function buildTimeline(historyPayload, phaseLabels, selectedCountry = null) {
  const months = (historyPayload.months ?? [])
    .map((month) => {
      const entries = (month.countries ?? [])
        .filter((entry) => !selectedCountry || entry.country === selectedCountry)
        .map(
          (entry) => `
            <div class="timeline-pill">
              <strong>${entry.country}</strong>
              <span>${phaseLabels[entry.phase] ?? entry.phase}</span>
              <small>${entry.as_of}</small>
            </div>
          `,
        )
        .join("");

      if (!entries) {
        return "";
      }

      return `
        <article class="timeline-card">
          <div class="timeline-month">${month.month}</div>
          <div class="timeline-track">${entries}</div>
        </article>
      `;
    })
    .join("");

  return `
    <section class="history-panel">
      <div class="section-heading">
        <p class="eyebrow">History Timeline</p>
        <h2>Recent cycle movement</h2>
        <p>Monthly history generated from <code>data/history/index.json</code>.</p>
      </div>
      <div class="timeline-grid">${months}</div>
    </section>
  `;
}

function buildObservationGrid(country) {
  const metrics = Object.entries(country.observations ?? {})
    .map(
      ([key, value]) => `
        <div class="metric-card">
          <span class="metric-label">${labelize(key)}</span>
          <strong class="metric-value">${formatValue(value)}</strong>
        </div>
      `,
    )
    .join("");

  return `
    <section class="observation-panel">
      <div class="section-heading">
        <p class="eyebrow">Observation Deck</p>
        <h2>Current readings</h2>
        <p>These are the raw operational inputs behind the unified phase label.</p>
      </div>
      <div class="metric-grid">${metrics}</div>
    </section>
  `;
}

function buildStrategySections(countryHandbook) {
  const sections = (countryHandbook.lenses ?? [])
    .map(
      (lens) => `
        <article class="strategy-card">
          <div class="strategy-topline">${lens.school}</div>
          <h3>${lens.title}</h3>
          <p class="strategy-summary">${lens.book}</p>
          <dl class="strategy-grid">
            <div>
              <dt>定義</dt>
              <dd>${lens.definition}</dd>
            </div>
            <div>
              <dt>現象</dt>
              <dd>${lens.phenomena}</dd>
            </div>
            <div>
              <dt>指標</dt>
              <dd>${lens.indicators}</dd>
            </div>
            <div>
              <dt>操作策略</dt>
              <dd>${lens.strategy}</dd>
            </div>
          </dl>
        </article>
      `,
    )
    .join("");

  return `
    <section class="strategy-panel">
      <div class="section-heading">
        <p class="eyebrow">Interpretive Lenses</p>
        <h2>Three masters, one operating phase</h2>
        <p>These sections interpret the site’s unified phase. They do not assert that the three books use identical native phase labels.</p>
      </div>
      <div class="strategy-stack">${sections}</div>
    </section>
  `;
}

function buildLanding(payload, historyPayload, siteContent, config) {
  const links = siteLinks(config);
  const countryCards = payload.countries
    .map((country) => {
      const href = country.country === "TW" ? links.tw : links.us;
      const handbook = siteContent.countries?.[country.country]?.handbook_by_phase?.[country.decision.final_phase];
      return `
        <a class="country-link-card" href="${href}">
          <p class="country-kicker">${handbook?.country_label ?? country.country}</p>
          <h3>${country.country === "TW" ? "Taiwan 台灣" : "United States 美國"}</h3>
          <p>${country.decision.reasons?.[0] ?? "Open the strategy page for the full playbook."}</p>
          <div class="country-phase-row">
            <span class="phase-badge">${handbook?.phase_label ?? country.decision.final_phase}</span>
            <span class="country-date">${country.as_of}</span>
          </div>
        </a>
      `;
    })
    .join("");

  const timelinePhases = (siteContent.home?.timeline ?? [])
    .map(
      (phase) => `
        <article class="phase-map-card tone-${phase.phase.toLowerCase()}">
          <p class="phase-map-label">${phase.label}</p>
          <div class="phase-lens-list">
            ${phase.lenses
              .map(
                (lens) => `
                  <div class="phase-lens-item">
                    <strong>${lens.title}</strong>
                    <span>${lens.focus}</span>
                  </div>
                `,
              )
              .join("")}
          </div>
        </article>
      `,
    )
    .join("");

  return `
    ${buildNav(config)}
    <main class="page">
      <section class="hero hero-map">
        <div class="hero-copy">
          <p class="eyebrow">Cycle Map Manual</p>
          <h1>${siteContent.home.hero.title}</h1>
          <p class="subtitle">${siteContent.home.hero.subtitle}</p>
        </div>
        <div class="hero-panel">
          <p class="hero-note">Method note</p>
          <p>${siteContent.home.method_notice.zh}</p>
        </div>
      </section>
      ${buildStatus(payload)}
      <section class="map-panel">
        <div class="section-heading">
          <p class="eyebrow">Cycle Timeline</p>
          <h2>One sequence, three interpretive lenses</h2>
          <p>${siteContent.home.method_notice.en}</p>
        </div>
        ${buildPhaseRail(siteContent.home.timeline, null)}
        <div class="phase-map">${timelinePhases}</div>
      </section>
      <section class="country-manuals">
        <div class="section-heading">
          <p class="eyebrow">Country Manuals</p>
          <h2>Open Taiwan or United States</h2>
          <p>Each country page uses the same template, then interprets the current phase through the three masters.</p>
        </div>
        <div class="country-grid">${countryCards}</div>
      </section>
      ${buildTimeline(historyPayload, Object.fromEntries(siteContent.home.timeline.map((item) => [item.phase, item.label])))}
    </main>
  `;
}

function buildCountryPage(payload, historyPayload, siteContent, config) {
  const country = payload.countries.find((entry) => entry.country === config.country);
  if (!country) {
    throw new Error(`Country ${config.country} not found in latest payload`);
  }

  const handbook = country.handbook ?? siteContent.countries?.[config.country]?.handbook_by_phase?.[country.decision.final_phase];
  const phaseLabels = Object.fromEntries(siteContent.home.timeline.map((item) => [item.phase, item.label]));
  const reasons = (country.decision.reasons ?? []).map((reason) => `<li>${reason}</li>`).join("");

  return `
    ${buildNav(config)}
    <main class="page">
      <section class="hero hero-country">
        <div class="hero-copy">
          <p class="eyebrow">Country Strategy Manual</p>
          <h1>${handbook.country_label}</h1>
          <p class="subtitle">Current phase, author interpretations, history, and raw inputs.</p>
        </div>
        <aside class="hero-panel phase-panel">
          <p class="phase-panel-label">Current operating phase</p>
          <div class="hero-phase">${handbook.phase_label}</div>
          <p class="country-date">As of ${country.as_of}</p>
          <p class="watch-copy">Watch: ${country.decision.watch ?? "none"}</p>
        </aside>
      </section>
      ${buildStatus(payload)}
      <section class="current-phase-panel">
        <div class="section-heading">
          <p class="eyebrow">Unified Positioning</p>
          <h2>Where the market sits today</h2>
          <p>${siteContent.home.method_notice.zh}</p>
        </div>
        ${buildPhaseRail(siteContent.home.timeline, country.decision.final_phase)}
        <div class="reason-box">
          <h3>Why this phase?</h3>
          <ul class="reasons">${reasons}</ul>
        </div>
      </section>
      ${buildStrategySections(handbook)}
      ${buildTimeline(historyPayload, phaseLabels, country.country)}
      ${buildObservationGrid(country)}
    </main>
  `;
}

async function loadApplication() {
  const config = getBodyConfig();
  const payload = await fetchJson(`${config.root}/data/latest.json`);
  const historyPayload = await fetchJson(`${config.root}/data/history/index.json`);
  const siteContent = await fetchJson(`${config.root}/data/site-content.json`);
  const app = document.getElementById("app");

  if (config.page === "country") {
    app.innerHTML = buildCountryPage(payload, historyPayload, siteContent, config);
    return;
  }

  app.innerHTML = buildLanding(payload, historyPayload, siteContent, config);
}

loadApplication().catch((error) => {
  const app = document.getElementById("app");
  app.innerHTML = `
    <main class="page">
      <section class="hero">
        <p class="eyebrow">Load Failure</p>
        <h1>Data load failed</h1>
        <p class="subtitle">${error.message}</p>
      </section>
    </main>
  `;
});
