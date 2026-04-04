from dataclasses import dataclass, field


@dataclass(slots=True)
class DecisionRecord:
    country: str
    as_of: str
    candidate_phase: str
    final_phase: str
    watch: str | None = None
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TransitionDecision:
    final_phase: str
    watch: str | None = None


@dataclass(slots=True)
class CandidateDecision:
    phase: str
    reasons: list[str] = field(default_factory=list)
