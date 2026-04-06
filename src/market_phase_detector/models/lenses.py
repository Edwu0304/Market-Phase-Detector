from dataclasses import dataclass, field


def _format_metric_value(value: float | int | str, display_format: str) -> str:
    if isinstance(value, str):
        return value
    if display_format == "percent":
        return f"{value:.1f}%"
    if display_format == "spread":
        return f"{value:.2f}"
    if display_format == "score":
        return f"{int(round(value))}"
    if display_format == "decimal":
        return f"{value:.2f}"
    return f"{value}"


@dataclass(slots=True)
class LensMetric:
    metric_id: str
    label: str
    value: float | int | str
    display_format: str
    status: str
    proxy_label: str | None = None

    def to_dict(self) -> dict:
        payload = {
            "id": self.metric_id,
            "label": self.label,
            "value": self.value,
            "display_value": _format_metric_value(self.value, self.display_format),
            "display_format": self.display_format,
            "status": self.status,
        }
        if self.proxy_label:
            payload["proxy_label"] = self.proxy_label
        return payload


@dataclass(slots=True)
class LensDecision:
    lens_id: str
    title: str
    phase: str
    phase_label: str
    reasons: list[str] = field(default_factory=list)
    metrics: list[LensMetric] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.lens_id,
            "title": self.title,
            "phase": self.phase,
            "phase_label": self.phase_label,
            "reasons": list(self.reasons),
            "metrics": [metric.to_dict() for metric in self.metrics],
        }


@dataclass(slots=True)
class LensHistoryRow:
    month: str
    as_of: str
    phase: str
    phase_label: str
    reasons: list[str] = field(default_factory=list)
    metrics: list[LensMetric] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "as_of": self.as_of,
            "phase": self.phase,
            "phase_label": self.phase_label,
            "reasons": list(self.reasons),
            "metrics": [metric.to_dict() for metric in self.metrics],
        }


@dataclass(slots=True)
class CountryLensBundle:
    current: LensDecision
    history: list[LensHistoryRow] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload = self.current.to_dict()
        payload["history"] = [row.to_dict() for row in self.history]
        return payload


@dataclass(slots=True)
class TransposedMetricRow:
    """A single metric with its values across time, for izaax transposed table."""
    metric_id: str
    label: str
    display_format: str
    is_transition_key: bool  # Whether this metric is critical for phase transition
    transition_direction: str  # "next" if it would push to next phase, "prev" if warning
    values: list[dict] = field(default_factory=list)  # [{"month": "2026-01", "display_value": "0.38", "status": "positive"}, ...]

    def to_dict(self) -> dict:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "display_format": self.display_format,
            "is_transition_key": self.is_transition_key,
            "transition_direction": self.transition_direction,
            "values": self.values,
        }


@dataclass(slots=True)
class IzaaxTransposedBundle:
    """Transposed Izaax data: metrics as rows, months as columns."""
    current_phase: str
    current_phase_label: str
    next_phase: str  # Next phase in sequence
    prev_phase: str  # Previous phase in sequence
    phase_sequence: list[str]  # Full sequence
    transition_keys: list[str]  # Which metric_ids are critical for next transition
    metric_rows: list[TransposedMetricRow]
    months: list[str]  # Month labels
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "current_phase": self.current_phase,
            "current_phase_label": self.current_phase_label,
            "next_phase": self.next_phase,
            "prev_phase": self.prev_phase,
            "phase_sequence": self.phase_sequence,
            "transition_keys": self.transition_keys,
            "metric_rows": [r.to_dict() for r in self.metric_rows],
            "months": self.months,
            "reasons": self.reasons,
        }
