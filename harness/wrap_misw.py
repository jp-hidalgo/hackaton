"""Optional read-only probe of the MISW4412 class agent.

Does not invoke the LLM and does not print secrets. It asks: if this agent's
configured base URLs sat in front of the July-style PEP, which ones would
count as unexpected egress?
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from harness.pep import Event, Policy

DEFAULT_ROOT = Path(r"C:\Users\jphid\OneDrive\Documents\GitHub\202620-MISW4412-GRUPO11")


@dataclass
class ToolProbe:
    name: str
    dest: str | None
    verdict: str
    control_id: str
    reason: str


def agent_root() -> Path | None:
    raw = os.getenv("MISW4412_ROOT")
    path = Path(raw) if raw else DEFAULT_ROOT
    if (path / "contract.py").is_file():
        return path
    return None


def probe_class_agent(root: Path | None = None) -> list[ToolProbe]:
    root = root or agent_root()
    if root is None:
        raise FileNotFoundError("MISW4412_ROOT not set and default class repo not found")

    sys.path.insert(0, str(root))
    try:
        from contract import get_settings, get_tools
    except Exception as exc:  # pragma: no cover - import environment
        raise RuntimeError(f"could not import class agent contract: {exc}") from exc

    settings = get_settings()
    tools = get_tools()
    policy = Policy(
        allow_hosts={"localhost", "127.0.0.1"},
        harness_mode=False,
    )

    dest_by_hint = {
        "consultar_productos": getattr(settings, "api_base_url", None),
        "consultar_perfil_cliente": getattr(settings, "api_base_url", None),
        "autenticar_cliente": getattr(settings, "api_base_url", None),
        "consultar_politicas": getattr(settings, "rag_base_url", None),
        "estimar_capacidad_ahorro": None,
        "simular_cuota_credito": None,
        "comparar_cuota_con_capacidad": None,
    }

    probes: list[ToolProbe] = []
    for tool in tools:
        name = getattr(tool, "name", None) or getattr(tool, "__name__", "unknown")
        dest = dest_by_hint.get(name)
        event = Event(
            step=1,
            zone="A",
            phase="class-agent-probe",
            action="http_get" if dest else "local",
            tool=name,
            dest=dest,
            workload_id="misw4412-finanzas",
        )
        decision = policy.mediate(event)
        probes.append(
            ToolProbe(
                name=name,
                dest=_host_only(dest),
                verdict=decision.verdict,
                control_id=decision.control_id,
                reason=decision.reason,
            )
        )
    return probes


def _host_only(url: str | None) -> str | None:
    if not url:
        return None
    raw = url if "://" in url else "https://" + url
    host = urlparse(raw).hostname
    return host
