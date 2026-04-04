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

async function loadDashboard() {
  const response = await fetch("./data/latest.json");
  const payload = await response.json();
  const root = document.getElementById("summary");
  const status = document.getElementById("status");
  const timelineRoot = document.getElementById("timeline");

  root.innerHTML = "";
  status.innerHTML = "";
  timelineRoot.innerHTML = "";

  const source = payload.meta?.source ?? "unknown";
  const sourcePill = document.createElement("div");
  sourcePill.className = "status-pill";
  sourcePill.textContent = `Source: ${source}`;
  status.appendChild(sourcePill);

  const generatedPill = document.createElement("div");
  generatedPill.className = "status-pill";
  generatedPill.textContent = `Generated: ${payload.generated_at}`;
  status.appendChild(generatedPill);

  if (payload.meta?.error) {
    const errorPill = document.createElement("div");
    errorPill.className = "status-pill meta-error";
    errorPill.textContent = `Fallback reason: ${payload.meta.error}`;
    status.appendChild(errorPill);
  }

  try {
    const historyResponse = await fetch("./data/history/index.json");
    const historyPayload = await historyResponse.json();
    for (const month of historyPayload.months ?? []) {
      const monthRow = document.createElement("div");
      monthRow.className = "timeline-month";

      const monthLabel = document.createElement("div");
      monthLabel.className = "timeline-month-label";
      monthLabel.textContent = month.month;
      monthRow.appendChild(monthLabel);

      const countryList = document.createElement("div");
      countryList.className = "timeline-country-list";
      for (const country of month.countries ?? []) {
        const pill = document.createElement("div");
        pill.className = "timeline-country-pill";
        pill.innerHTML = `<strong>${country.country}</strong> ${country.phase}`;
        countryList.appendChild(pill);
      }
      monthRow.appendChild(countryList);

      timelineRoot.appendChild(monthRow);
    }
  } catch (error) {
    const empty = document.createElement("div");
    empty.className = "status-pill";
    empty.textContent = `Timeline unavailable: ${error.message}`;
    timelineRoot.appendChild(empty);
  }

  for (const country of payload.countries) {
    const card = document.createElement("article");
    card.className = "card";

    const reasons = country.decision.reasons
      .map((reason) => `<li>${reason}</li>`)
      .join("");

    const observations = Object.entries(country.observations)
      .map(
        ([key, value]) => `
          <div class="metric">
            <span class="metric-label">${labelize(key)}</span>
            <span class="metric-value">${formatValue(value)}</span>
          </div>
        `,
      )
      .join("");

    card.innerHTML = `
      <h2>${country.country}</h2>
      <p class="phase">${country.decision.final_phase}</p>
      <p class="watch">Watch: ${country.decision.watch ?? "none"}</p>
      <p class="date">As of ${country.as_of}</p>
      <ul class="reasons">${reasons}</ul>
      <div class="metrics">${observations}</div>
    `;

    root.appendChild(card);
  }
}

loadDashboard().catch((error) => {
  const root = document.getElementById("summary");
  root.innerHTML = `<article class="card"><h2>Data load failed</h2><p>${error.message}</p></article>`;
});
