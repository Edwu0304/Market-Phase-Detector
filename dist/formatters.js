export function formatDirection(value) {
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

export function formatScalar(value) {
  if (typeof value === "string") {
    return formatDirection(value);
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  return String(value);
}
