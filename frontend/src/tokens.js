export function phaseTone(phase) {
  return `phase-${String(phase).toLowerCase()}`;
}

export function phaseLabel(phase) {
  const labels = {
    Recovery: "復甦",
    Growth: "成長",
    Boom: "榮景",
    Recession: "衰退",
  };
  return labels[phase] ?? phase;
}

export function nextPhase(phase) {
  const phases = ["Recovery", "Growth", "Boom", "Recession"];
  const index = phases.indexOf(phase);
  return index === -1 ? phase : phases[(index + 1) % phases.length];
}

export function labelizeMetricKey(key) {
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
