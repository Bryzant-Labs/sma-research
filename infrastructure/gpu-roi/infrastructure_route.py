"""GPU ROI benchmark endpoints.

Public, DB-independent endpoints that serve the sanitized GPU ROI dataset
committed in the sma-research public repo. The backing JSONs are bundled
with the deployment and refreshed manually; rendering happens at request
time so any new row is reflected within one cache-TTL (5 minutes).

Endpoints:
- GET  /infrastructure/gpu-roi                 — full ROI table (list of rows)
- GET  /infrastructure/workload-compatibility  — 21 workloads x 10 GPU columns
- GET  /infrastructure/silent-zero             — workloads with gate_pass_rate <= 0.5
- POST /infrastructure/pick                    — routes via gpu_picker.best_gpu_for()
- GET  /infrastructure/workloads               — list of known workload names (for picker UI)
"""

from __future__ import annotations

import json
import logging
from importlib import util as importlib_util
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Data location — public copy bundled with deployment.
# Resolves to <repo-root>/data/gpu-roi/ when sma-research data is rsync'd there,
# or falls back to a dev path for local testing.
# ---------------------------------------------------------------------------

_CANDIDATE_DIRS = [
    Path("/home/bryzant/sma-platform/data/gpu-roi"),
    Path("/home/bryzant/sma-research/infrastructure/gpu-roi"),
    Path(__file__).resolve().parents[3] / "data" / "gpu-roi",
]


def _data_dir() -> Path:
    for p in _CANDIDATE_DIRS:
        if p.is_dir() and (p / "gpu_roi_table.json").is_file():
            return p
    raise HTTPException(
        status_code=503,
        detail=(
            "GPU ROI dataset not installed on this deployment. "
            "Expected gpu_roi_table.json under one of: "
            f"{[str(p) for p in _CANDIDATE_DIRS]}"
        ),
    )


_CACHE_SECONDS = 300  # 5 minutes — honours manual refresh cadence
_CACHE_HEADERS = {
    "Cache-Control": f"public, max-age={_CACHE_SECONDS}, stale-while-revalidate=60",
}


def _load_json(name: str) -> dict[str, Any]:
    path = _data_dir() / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"{name} not found")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        logger.error("Failed to parse %s: %s", path, e)
        raise HTTPException(status_code=500, detail=f"{name} is not valid JSON")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/infrastructure/gpu-roi")
async def gpu_roi_table(response: Response):
    """Full measured ROI table. One row per (workload, GPU) with n_tasks >= 5."""
    data = _load_json("gpu_roi_table.json")
    for k, v in _CACHE_HEADERS.items():
        response.headers[k] = v
    return data


@router.get("/infrastructure/workload-compatibility")
async def workload_compatibility(response: Response):
    """21 workloads x 10 GPU columns compatibility matrix + enriched per-cell measurements."""
    data = _load_json("workload_compatibility.json")
    for k, v in _CACHE_HEADERS.items():
        response.headers[k] = v
    return data


@router.get("/infrastructure/silent-zero")
async def silent_zero_warnings(response: Response):
    """Workloads with observed gate-pass rate <= 50%. Skip these unless upstream is fixed."""
    data = _load_json("silent_zero_warnings.json")
    for k, v in _CACHE_HEADERS.items():
        response.headers[k] = v
    return data


@router.get("/infrastructure/workloads")
async def list_workloads(response: Response):
    """List of workload names known to the picker (for dropdown UIs).

    Union of compatibility-matrix keys and ROI-table workloads, because some
    workloads appear in one but not the other (e.g. ROI tracks MD at specific
    atom-count tiers while compat uses a single 'openmm_md_production' row).
    Flags which side has measured data.
    """
    compat = _load_json("workload_compatibility.json")
    roi = _load_json("gpu_roi_table.json")

    compat_names = set((compat.get("workloads") or {}).keys())
    roi_names = {r["workload"] for r in roi.get("rows", [])}

    all_names = sorted(compat_names | roi_names)
    details = [
        {
            "name": n,
            "in_compat_matrix": n in compat_names,
            "has_roi_rows": n in roi_names,
        }
        for n in all_names
    ]

    for k, v in _CACHE_HEADERS.items():
        response.headers[k] = v
    return {
        "count": len(all_names),
        "workloads": all_names,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Picker
# ---------------------------------------------------------------------------

class PickRequest(BaseModel):
    workload: str = Field(..., description="Workload name, e.g. 'boltz2_rescore_streaming'")
    problem_size: int | None = Field(
        default=None,
        description="Problem size (e.g. residues, atoms). Filtered against memory_ceiling.",
    )
    deadline_sec: int | None = Field(
        default=None, description="Optional deadline — not currently used for ranking."
    )
    prefer_free: bool = Field(
        default=True,
        description="Prefer hosted NIM free tier when quota > batch_size.",
    )
    batch_size: int = Field(
        default=1000,
        ge=1,
        le=1_000_000,
        description="Batch size used to amortize warmup cost.",
    )
    concurrent_n: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Current queue depth for the endpoint (affects contention penalty).",
    )


def _load_picker_module():
    """Dynamically load gpu_picker.py next to the data JSONs.

    The picker is committed under the same directory as the JSONs for
    reproducibility. We load by file path rather than importing to avoid
    coupling the platform backend with the fleet-side Python package layout.
    """
    path = _data_dir() / "gpu_picker.py"
    if not path.is_file():
        raise HTTPException(status_code=503, detail="gpu_picker.py not installed")
    spec = importlib_util.spec_from_file_location("sma_gpu_picker", path)
    if spec is None or spec.loader is None:
        raise HTTPException(status_code=500, detail="Cannot load gpu_picker.py")
    mod = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@router.post("/infrastructure/pick")
async def infrastructure_pick(body: PickRequest, response: Response):
    """Rank the top-3 GPU options for a workload, using gpu_picker.best_gpu_for().

    Returns a structure that always contains `options: list` even when no
    option matches — in that case the list holds a single advisory row.
    """
    picker = _load_picker_module()
    try:
        options = picker.best_gpu_for(
            workload=body.workload,
            problem_size=body.problem_size,
            deadline_sec=body.deadline_sec,
            prefer_free=body.prefer_free,
            batch_size=body.batch_size,
            concurrent_n=body.concurrent_n,
        )
    except Exception as e:  # keep error surface narrow
        logger.exception("picker failed for workload=%s", body.workload)
        raise HTTPException(status_code=400, detail=f"picker error: {e}")

    # Short cache — picker output depends on body, so we keep it low but non-zero
    response.headers["Cache-Control"] = "public, max-age=60"
    return {
        "workload": body.workload,
        "problem_size": body.problem_size,
        "batch_size": body.batch_size,
        "concurrent_n": body.concurrent_n,
        "prefer_free": body.prefer_free,
        "options": options,
    }
