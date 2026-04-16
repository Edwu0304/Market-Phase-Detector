import { formatDirection, formatScalar } from "./formatters.js";
import { labelizeMetricKey, phaseLabel, phaseTone } from "./tokens.js";
import { renderCountryPage } from "./pages/renderCountry.js";
import { renderLanding } from "./pages/renderLanding.js";
import { renderFatalLoadError } from "./pages/shared.js";

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

async function loadApplication() {
  void formatDirection;
  void formatScalar;
  void labelizeMetricKey;
  void phaseLabel;
  void phaseTone;

  const config = getBodyConfig();
  const payload = await fetchJson(`${config.root}/data/latest.json`);
  const siteContent = await fetchJson(`${config.root}/data/site-content.json`);
  const app = document.getElementById("app");

  if (config.page === "country") {
    renderCountryPage(payload, siteContent, config);
    return;
  }

  app.innerHTML = renderLanding(payload, siteContent, config);
}

loadApplication().catch((error) => {
  document.getElementById("app").innerHTML = renderFatalLoadError(error);
});
