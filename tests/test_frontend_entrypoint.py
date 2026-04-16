from pathlib import Path


def test_frontend_entrypoint_exists():
    assert Path("frontend/src/index.html").exists()


def test_country_pages_exist():
    assert Path("frontend/src/tw/index.html").exists()
    assert Path("frontend/src/us/index.html").exists()


def test_frontend_shell_mentions_module_entrypoint_and_navigation():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    landing_renderer = Path("frontend/src/pages/renderLanding.js").read_text(encoding="utf-8")
    country_renderer = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    country_components = Path("frontend/src/domain/country.js").read_text(encoding="utf-8")

    assert 'import { renderLanding } from "./pages/renderLanding.js"' in script
    assert 'import { renderCountryPage } from "./pages/renderCountry.js"' in script
    assert "renderLanding(payload, siteContent, config)" in script
    assert "renderCountryPage(payload, siteContent, config)" in script
    assert "buildLanding" in landing_renderer
    assert "buildCountryShell" in country_renderer
    assert "terminal-hero" in landing_renderer
    assert "country-status-band" in country_components


def test_frontend_uses_extracted_tokens_and_formatters():
    tokens = Path("frontend/src/tokens.js").read_text(encoding="utf-8")
    formatters = Path("frontend/src/formatters.js").read_text(encoding="utf-8")
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")

    assert "export function phaseTone" in tokens
    assert "export function phaseLabel" in tokens
    assert "export function labelizeMetricKey" in tokens
    assert "export function formatDirection" in formatters
    assert "export function formatScalar" in formatters
    assert 'from "./tokens.js"' in script
    assert 'from "./formatters.js"' in script


def test_frontend_uses_domain_component_modules():
    landing_components = Path("frontend/src/domain/landing.js").read_text(encoding="utf-8")
    country_components = Path("frontend/src/domain/country.js").read_text(encoding="utf-8")
    lens_components = Path("frontend/src/domain/lens.js").read_text(encoding="utf-8")
    landing_renderer = Path("frontend/src/pages/renderLanding.js").read_text(encoding="utf-8")
    country_renderer = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")

    assert "export function renderCountrySummaryCard" in landing_components
    assert "export function renderOverviewTicker" in landing_components
    assert "export function renderLensFrameworkStrip" in landing_components
    assert "export function renderObservationChip" in country_components
    assert "export function renderCountryStatusBand" in country_components
    assert "export function renderSitePhasePanel" in country_components
    assert "export function renderPhaseBadge" in lens_components
    assert "export function renderLensDecisionPanel" in lens_components
    assert "Support Current Phase" in lens_components
    assert "Support Next Phase" in lens_components
    assert "Conflict Signals" in lens_components
    assert 'from "../domain/landing.js"' in landing_renderer
    assert 'from "../domain/country.js"' in country_renderer
    assert 'from "../domain/lens.js"' in country_renderer


def test_frontend_terminal_layout_mentions_workspace_markers():
    landing_renderer = Path("frontend/src/pages/renderLanding.js").read_text(encoding="utf-8")
    country_renderer = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    landing_components = Path("frontend/src/domain/landing.js").read_text(encoding="utf-8")
    lens_components = Path("frontend/src/domain/lens.js").read_text(encoding="utf-8")

    assert "market-overview-strip" in landing_renderer
    assert "country-gateway-grid" in landing_renderer
    assert "lens-framework-strip" in landing_components
    assert "country-command-header" in country_renderer
    assert "lens-workspace-stack" in country_renderer
    assert "lens-workspace" in lens_components
