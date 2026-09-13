"""Run the class agent locally: tools first, then one LLM turn, then PEP check."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CLASS_ROOT = Path(r"C:\Users\jphid\OneDrive\Documents\GitHub\202620-MISW4412-GRUPO11")
HACK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLASS_ROOT))
sys.path.insert(0, str(HACK_ROOT))


def _print(title: str, payload) -> None:
    print(f"\n=== {title} ===")
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:2000])
    else:
        print(str(payload)[:2000])


def test_tools() -> dict:
    from agent.tools import get_local_tools

    tools = {t.name: t for t in get_local_tools()}
    results = {}
    results["consultar_productos"] = tools["consultar_productos"].invoke(
        {"tipo_producto": "ahorros"}
    )
    results["simular_cuota_credito"] = tools["simular_cuota_credito"].invoke(
        {"monto": 20_000_000, "tasa_ea": 18.9, "plazo_meses": 36}
    )
    results["autenticar_cliente"] = tools["autenticar_cliente"].invoke(
        {"documento": "1032456789", "clave": "2001"}
    )
    for name, payload in results.items():
        _print(f"tool {name}", payload)
    return results


def test_llm_turn() -> dict:
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    from agent.graph import build_graph
    from agent.tools import get_local_tools

    graph = build_graph(tools=get_local_tools())
    state = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Simula un credito de 20000000 COP a 18.9% EA a 36 meses."
                )
            ]
        },
        config={"recursion_limit": 12},
    )
    transcript = []
    for message in state.get("messages") or []:
        if isinstance(message, HumanMessage):
            transcript.append({"role": "user", "text": message.content})
        elif isinstance(message, ToolMessage):
            transcript.append(
                {"role": "tool", "name": message.name, "text": str(message.content)[:400]}
            )
        elif isinstance(message, AIMessage):
            transcript.append(
                {
                    "role": "assistant",
                    "text": message.content,
                    "tools": [c.get("name") for c in (message.tool_calls or [])],
                }
            )
    _print("llm turn", transcript)
    return {"ok": True, "turns": len(transcript), "transcript": transcript}


def test_pep_on_live_tools(tool_results: dict) -> list[dict]:
    from harness.pep import Event, Policy

    policy = Policy(allow_hosts={"localhost", "127.0.0.1", "pypi.org"})
    events = [
        Event(
            1,
            "A",
            "class-agent",
            "http_get",
            "consultar_productos",
            dest="http://localhost:8080/finanzas/productos",
        ),
        Event(
            2,
            "A",
            "class-agent",
            "local",
            "simular_cuota_credito",
            args=tool_results["simular_cuota_credito"],
        ),
        Event(
            3,
            "A",
            "class-agent",
            "http_get",
            "consultar_politicas",
            dest="http://34.71.149.196:8000/api/v1",
        ),
    ]
    rows = []
    for event in events:
        decision = policy.mediate(event)
        row = {
            "tool": event.tool,
            "verdict": decision.verdict,
            "control": decision.control_id,
            "reason": decision.reason,
        }
        rows.append(row)
        _print("pep", row)
    return rows


def main() -> int:
    print("class root:", CLASS_ROOT)
    tools = test_tools()
    pep = test_pep_on_live_tools(tools)
    llm = test_llm_turn()
    out = HACK_ROOT / "artifact" / "live-agent-run.json"
    out.write_text(
        json.dumps(
            {
                "tools": tools,
                "pep": pep,
                "llm": {
                    "ok": llm["ok"],
                    "turns": llm["turns"],
                    "transcript": llm["transcript"],
                },
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
