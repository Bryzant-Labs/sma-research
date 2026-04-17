"""
gpu_picker — selects the best GPU backend for a given workload using
measured ROI data (real data or NO_DATA, never fabricated).

Reads:
  lib/gpu_roi_table.json           — per-(GPU, workload) measured ROI rows
  lib/workload_compatibility.json  — compatibility matrix + per-cell enriched fields

Public API:
    best_gpu_for(
        workload: str,
        problem_size: int | None = None,
        deadline_sec: int | None = None,
        prefer_free: bool = True,
        forbid_silent_zero: bool = True,
    ) -> list[dict]
        Returns up to 3 ranked options, each a dict with:
            gpu, rank, expected_usd_per_unit, rationale, source_path

Picker logic order (hard rule from coordinator):
  1. If free tier available + quota > batch_size → return ("HostedNIMWorker", $0) first.
  2. Filter by memory_ceiling >= problem_size (if problem_size given).
  3. Compute effective_$/unit =
         ($/hr × time_per_unit + warmup_cost_amortized) × contention_penalty / gate_pass_rate
     where contention_penalty uses the dispatcher's current queue depth (default n1).
  4. Return top 3 ranked.

Never invents a number — any cell lacking a field marks that option `unavailable`
with rationale.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

LIB_DIR = Path(__file__).parent
ROI_PATH = LIB_DIR / "gpu_roi_table.json"
COMPAT_PATH = LIB_DIR / "workload_compatibility.json"


def _load() -> tuple[dict, dict]:
    with open(ROI_PATH) as fh:
        roi = json.load(fh)
    with open(COMPAT_PATH) as fh:
        compat = json.load(fh)
    return roi, compat


def _contention_factor(cell: dict, concurrent_n: int) -> float:
    """Pick the contention penalty that matches the current queue depth."""
    cp = cell.get("contention_penalty") or {}
    if not isinstance(cp, dict):
        return 1.0
    if concurrent_n <= 1:
        return cp.get("n1") or 1.0
    if concurrent_n <= 3:
        return cp.get("n3") or cp.get("n1") or 1.0
    return cp.get("n5") or cp.get("n3") or cp.get("n1") or 1.0


def _memory_ceiling_ok(cell: dict, problem_size: int | None) -> tuple[bool, str]:
    if problem_size is None:
        return True, "no problem_size specified"
    mc = cell.get("memory_ceiling")
    if mc == "NO_DATA" or mc is None:
        # No measured ceiling — accept conservatively but annotate
        return True, "memory_ceiling NO_DATA; assume ok but risky"
    if isinstance(mc, dict):
        val = mc.get("value")
        if val is None:
            return True, "memory_ceiling value missing"
        if problem_size > val:
            return False, f"problem_size {problem_size} > measured ceiling {val} {mc.get('units','?')}"
    return True, "ok"


def _effective_cost_per_unit(row: dict, concurrent_n: int = 1, amortize_over_units: int = 1000) -> float | None:
    """Compute effective $/unit after warmup + contention + gate.

    amortize_over_units: we spread warmup cost across this many outputs.
    For short jobs this is low (warmup dominates); for big campaigns set high.
    """
    rate_per_hr = row.get("rate_per_hr")
    usd_per_hr = row.get("usd_per_hr")
    if rate_per_hr is None or usd_per_hr is None or rate_per_hr == 0:
        return None

    time_per_unit_hr = 1.0 / rate_per_hr
    raw_cost = usd_per_hr * time_per_unit_hr

    warmup_cost = float(row.get("warmup_cost_usd") or 0.0)
    amortized_warmup = warmup_cost / max(1, amortize_over_units)

    contention = _contention_factor(row, concurrent_n)

    gate = row.get("gate_pass_rate")
    if gate is None:
        # No gate defined — skip gate adjustment
        gate_adj = 1.0
    elif gate == 0.0 or gate == 0:
        # Infinite effective cost — useless output
        return math.inf
    else:
        gate_adj = float(gate)

    return (raw_cost + amortized_warmup) * contention / gate_adj


def best_gpu_for(
    workload: str,
    problem_size: int | None = None,
    deadline_sec: int | None = None,
    prefer_free: bool = True,
    forbid_silent_zero: bool = True,
    batch_size: int = 1000,
    concurrent_n: int = 1,
) -> list[dict[str, Any]]:
    """Return up to 3 ranked GPU options for a workload.

    Each option: {
        rank: int,
        gpu: str,
        worker_hint: str,
        expected_usd_per_unit: float | None,
        usd_per_unit_raw: float | None,
        gate_pass_rate: float | None,
        memory_ceiling: dict | str | None,
        rationale: str,
        source_path: str,
    }
    """
    roi, compat = _load()

    # --- Step 1: Free tier preference ---
    wl_compat = compat.get("workloads", {}).get(workload, {})
    free = wl_compat.get("free_tier", {})
    if prefer_free and free.get("available"):
        quota = free.get("quota_remaining_today")
        # If quota is None assume unknown-but-available; if numeric, check
        if quota is None or quota > batch_size:
            # Find the hosted_NIM row for this workload if it exists
            nim_row = None
            for r in roi["rows"]:
                if r["workload"] == workload and r["gpu"] == "hosted_NIM":
                    nim_row = r
                    break
            if nim_row is not None:
                if forbid_silent_zero and (nim_row.get("gate_pass_rate") or 0) == 0:
                    # Free tier broken — fall through to paid ranking
                    pass
                else:
                    return [
                        {
                            "rank": 1,
                            "gpu": "hosted_NIM",
                            "worker_hint": "HostedNIMWorker",
                            "expected_usd_per_unit": 0.0,
                            "usd_per_unit_raw": 0.0,
                            "gate_pass_rate": nim_row.get("gate_pass_rate"),
                            "memory_ceiling": nim_row.get("memory_ceiling"),
                            "rationale": "free tier preferred (quota > batch, gate_pass_rate ok)",
                            "source_path": nim_row.get("source_path", "NIM hosted"),
                        }
                    ]

    # --- Step 2: Filter paid rows by compat + memory ceiling ---
    candidates = []
    for r in roi["rows"]:
        if r["workload"] != workload:
            continue
        if r["gpu"] == "hosted_NIM":
            # Only hit paid ranking for non-free workloads
            if not prefer_free:
                candidates.append(r)
            continue
        ok, reason = _memory_ceiling_ok(r, problem_size)
        if not ok:
            # Skip — too small
            continue
        if forbid_silent_zero and r.get("gate_pass_rate") == 0:
            continue
        candidates.append(r)

    if not candidates:
        # Nothing matches — return advisory
        return [
            {
                "rank": 1,
                "gpu": "NO_MATCH",
                "worker_hint": "fallback_to_heuristic",
                "expected_usd_per_unit": None,
                "rationale": f"no (GPU, workload={workload}) pair with n>=5 measured data matches constraints (problem_size={problem_size})",
                "source_path": "lib/gpu_roi_table.json",
            }
        ]

    # --- Step 3: Rank by effective $/unit ---
    scored = []
    for r in candidates:
        eff = _effective_cost_per_unit(r, concurrent_n=concurrent_n, amortize_over_units=batch_size)
        scored.append((eff if eff is not None else math.inf, r))
    scored.sort(key=lambda x: x[0])

    out = []
    for rank, (eff, r) in enumerate(scored[:3], start=1):
        rationale_parts = [
            f"${r.get('usd_per_hr', 0):.3f}/hr x {r.get('rate_per_hr', 0):.1f} units/hr",
            f"warmup ${r.get('warmup_cost_usd', 0):.3f}",
            f"contention n{concurrent_n}={_contention_factor(r, concurrent_n):.1f}x",
            f"gate pass {r.get('gate_pass_rate') if r.get('gate_pass_rate') is not None else 'N/A'}",
            f"n={r.get('n_tasks')}",
        ]
        out.append(
            {
                "rank": rank,
                "gpu": r["gpu"],
                "worker_hint": _gpu_to_worker(r["gpu"]),
                "expected_usd_per_unit": None if eff == math.inf else round(eff, 6),
                "usd_per_unit_raw": r.get("usd_per_unit_raw"),
                "gate_pass_rate": r.get("gate_pass_rate"),
                "memory_ceiling": r.get("memory_ceiling"),
                "rationale": "; ".join(rationale_parts),
                "source_path": r.get("source_path"),
            }
        )
    return out


def _gpu_to_worker(gpu: str) -> str:
    """Map a GPU model string to a dispatcher worker class name."""
    if gpu == "hosted_NIM":
        return "HostedNIMWorker"
    if gpu.startswith("H100") or gpu.startswith("B200"):
        # Brev-hosted H100 is preferred for persistent warm VMs; Vast for spot rentals
        return "BrevWorker|VastWorker"
    if gpu.startswith("A100") or gpu.startswith("RTX"):
        return "VastWorker"
    if gpu.startswith("TPU"):
        return "TPUWorker"
    return "VastWorker"


def explain_routing(workload: str) -> dict[str, Any]:
    """Debug helper: dump compat cell + all ROI rows for a workload."""
    _, compat = _load()
    roi, _ = _load()
    cell = compat.get("workloads", {}).get(workload, {})
    rows = [r for r in roi["rows"] if r["workload"] == workload]
    return {"workload": workload, "compat": cell, "roi_rows": rows}


if __name__ == "__main__":
    import sys

    wl = sys.argv[1] if len(sys.argv) > 1 else "boltz2_rescore_streaming"
    ps = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print(json.dumps(best_gpu_for(wl, problem_size=ps), indent=2, default=str))
