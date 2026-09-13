"""Synthetic replay of the public July 2026 shape.

Events name phases and destinations that Hugging Face and OpenAI already
published. They do not include payloads, constructors, or cache-poison recipes.
"""

from __future__ import annotations

from harness.pep import Event


def july_chain() -> list[Event]:
    return [
        Event(
            1,
            "A",
            "eval_package_install",
            "http_get",
            "fetch_package",
            dest="https://pypi.org/simple/requests",
            workload_id="eval-1",
            credential_id="proxy-shared",
        ),
        Event(
            2,
            "A",
            "eval_unexpected_egress",
            "http_get",
            "fetch_url",
            dest="https://huggingface.co/datasets/example",
            workload_id="eval-1",
            credential_id="proxy-shared",
        ),
        Event(
            3,
            "A",
            "proxy_admin",
            "privilege",
            "proxy_admin",
            workload_id="eval-1",
            credential_id="proxy-shared",
            flags=frozenset({"proxy_admin"}),
        ),
        Event(
            4,
            "A",
            "shared_identity",
            "http_get",
            "fetch_package",
            dest="https://pypi.org/simple/httpx",
            workload_id="eval-2",
            credential_id="proxy-shared",
        ),
        Event(
            5,
            "B",
            "harness_open_internet",
            "http_get",
            "harness_submit",
            dest="https://example.net/staging",
            workload_id="harness-1",
        ),
        Event(
            6,
            "B",
            "canary_in_harness",
            "read_env",
            "dump_env",
            args={"env": "CANARY-EVAL-TOKEN"},
            workload_id="harness-1",
        ),
        Event(
            7,
            "C",
            "dataset_local_path",
            "load_config",
            "load_dataset_config",
            args={"config": "split points at /proc/self/environ"},
            workload_id="worker-1",
        ),
        Event(
            8,
            "C",
            "imds",
            "http_get",
            "http_get",
            dest="http://169.254.169.254/latest/meta-data/",
            workload_id="worker-1",
        ),
        Event(
            9,
            "C",
            "c2_public_service",
            "http_post",
            "http_post",
            dest="https://pastebin.example/drop",
            workload_id="worker-1",
        ),
        Event(
            10,
            "C",
            "secret_canary",
            "read_secret",
            "read_secret",
            args={"name": "mesh-key", "value": "CANARY-EVAL-TOKEN"},
            workload_id="worker-1",
        ),
    ]


def recon_burst(n: int = 10) -> list[Event]:
    """Volume-only trace: individually boring GETs to an allowed host."""
    return [
        Event(
            i,
            "C",
            "recon",
            "recon",
            "http_get",
            dest="https://pypi.org/simple/probe",
            workload_id="worker-burst",
        )
        for i in range(1, n + 1)
    ]
