"""Replay engine: first blocking decision ends the chain."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from harness.pep import Decision, Event, Policy
from harness.traces import july_chain, recon_burst

DIGEST_PATH = Path(__file__).resolve().parents[1] / "artifact" / "egress-digest.json"


@dataclass
class ReplayResult:
    name: str
    stopped_at: int | None
    stop_control: str | None
    pages: list[str] = field(default_factory=list)
    log: list[dict] = field(default_factory=list)

    @property
    def stopped(self) -> bool:
        return self.stopped_at is not None


def replay(events: list[Event], policy: Policy | None = None, name: str = "run") -> ReplayResult:
    policy = policy or Policy()
    result = ReplayResult(name=name, stopped_at=None, stop_control=None)
    for event in events:
        decision = policy.mediate(event)
        result.log.append(
            {
                "step": event.step,
                "zone": event.zone,
                "phase": event.phase,
                "tool": event.tool,
                "dest": event.dest,
                "verdict": decision.verdict,
                "control": decision.control_id,
                "reason": decision.reason,
            }
        )
        if decision.page:
            result.pages.append(decision.control_id)
        if decision.blocks:
            result.stopped_at = event.step
            result.stop_control = decision.control_id
            break
    return result


def write_digest(results: list[ReplayResult], path: Path = DIGEST_PATH) -> Path:
    destinations: set[str] = set()
    for result in results:
        for row in result.log:
            if row.get("dest"):
                destinations.add(str(row["dest"]))
    body = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "v0.1-eval-egress",
        "destination_classes": sorted(_classify(d) for d in destinations),
        "destinations_redacted": [_redact(d) for d in sorted(destinations)],
        "runs": [
            {
                "name": r.name,
                "stopped_at": r.stopped_at,
                "stop_control": r.stop_control,
                "pages": r.pages,
            }
            for r in results
        ],
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    body["sha256"] = hashlib.sha256(encoded).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return path


def _classify(dest: str) -> str:
    lowered = dest.lower()
    if "169.254.169.254" in lowered:
        return "link-local-metadata"
    if "pastebin" in lowered or "webhook" in lowered:
        return "public-c2-class"
    if "huggingface.co" in lowered:
        return "public-platform"
    if "pypi.org" in lowered or "pythonhosted.org" in lowered:
        return "package-index"
    if "localhost" in lowered or "127.0.0.1" in lowered:
        return "loopback"
    return "other-public"


def _redact(dest: str) -> str:
    return _classify(dest)


def default_suite() -> list[ReplayResult]:
    lab = replay(july_chain(), Policy(), name="july-chain")
    burst = replay(recon_burst(10), Policy(burst_page_after=8), name="recon-burst")
    harness = replay(
        [e for e in july_chain() if e.zone == "B"],
        Policy(harness_mode=True),
        name="harness-mode",
    )
    return [lab, burst, harness]


def result_to_dict(result: ReplayResult) -> dict:
    return asdict(result)
