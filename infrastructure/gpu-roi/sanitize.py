"""
Sanitize gpu_roi_table.json + workload_compatibility.json for public release.

Removes:
  - Vast instance IDs (e.g., "35097680", "35141611") — leak rental history
  - Per-rental dollar totals (e.g., "19.68h $32.01") — aggregate to spend totals
  - Internal paths (e.g., "fleet-results/", "memory/") — implementation details

Keeps:
  - $/hr vendor prices (public marketplace data)
  - Throughput measurements (units/hr)
  - Gate-pass rates, warmup, contention, memory ceiling
  - Workload names, GPU model names
  - Generic source descriptions ("measured on A100 SXM4 rentals, Apr 2026")

Run:
    python sanitize.py ../../../gpu-fleet/lib/ .
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


INSTANCE_ID_RE = re.compile(r"\b3\d{7}\b")  # Vast instance IDs (8 digits starting with 3x)
DOLLAR_TOTAL_RE = re.compile(r"\$\d+\.\d{1,2}\b")  # per-rental $ totals
HOURS_TOTAL_RE = re.compile(r"\b\d+\.\d+h\b")  # e.g., "19.68h"


def _scrub_source(text: str) -> str:
    """Strip instance IDs, per-rental totals, and internal paths from a source string."""
    if not isinstance(text, str):
        return text

    # Remove instance ID references
    text = INSTANCE_ID_RE.sub("[instance]", text)

    # Remove per-rental $ totals (keeps $/hr since those don't match this pattern when followed by /hr)
    # Only scrub dollar amounts NOT followed by "/hr"
    def _strip_dollar(m: re.Match) -> str:
        end = m.end()
        if text[end:end + 3] == "/hr":
            return m.group(0)
        return "[amt]"

    text = DOLLAR_TOTAL_RE.sub(_strip_dollar, text)

    # Remove per-rental hours (we keep rate_per_hr metrics elsewhere)
    text = HOURS_TOTAL_RE.sub("[h]", text)

    # Rewrite common internal paths
    text = text.replace("fleet-results/", "fleet-logs/")
    text = text.replace("fleet-results", "fleet-logs")
    text = text.replace("memory/", "notes/")
    text = text.replace("vastai ", "vast.ai ")
    text = text.replace("vastai", "vast.ai")
    text = text.replace("gpu-fleet/logs/", "fleet-logs/")

    return text


def _scrub_obj(obj):
    """Recursively scrub any 'source', 'source_path', 'notes', 'warmup_source' string fields."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in {"source", "source_path", "notes", "warmup_source"}:
                out[k] = _scrub_source(v) if isinstance(v, str) else v
            else:
                out[k] = _scrub_obj(v)
        return out
    if isinstance(obj, list):
        return [_scrub_obj(x) for x in obj]
    return obj


def sanitize_roi(roi: dict) -> dict:
    """Sanitize the ROI table."""
    roi = _scrub_obj(roi)
    meta = roi.setdefault("_meta", {})
    meta["public_release"] = True
    meta["license"] = "CC-BY-4.0"
    meta["source_repo"] = "https://github.com/Bryzant-Labs/sma-research"
    meta["note"] = (
        "Public sanitized snapshot. Per-rental invoice references and "
        "dollar totals are redacted; $/hr vendor prices and throughput "
        "measurements are preserved."
    )
    return roi


def sanitize_compat(compat: dict) -> dict:
    """Sanitize the compatibility matrix."""
    compat = _scrub_obj(compat)
    meta = compat.setdefault("_meta", {})
    meta["public_release"] = True
    meta["license"] = "CC-BY-4.0"
    meta["source_repo"] = "https://github.com/Bryzant-Labs/sma-research"
    return compat


def derive_silent_zero(roi: dict) -> dict:
    """Extract silent-zero warnings (gate_pass_rate == 0) as a standalone payload."""
    warnings = []
    for row in roi.get("rows", []):
        gate = row.get("gate_pass_rate")
        if gate is None:
            continue
        try:
            gate_val = float(gate)
        except (TypeError, ValueError):
            continue
        if gate_val <= 0.5:
            warnings.append(
                {
                    "workload": row["workload"],
                    "gpu": row["gpu"],
                    "gate_pass_rate": gate_val,
                    "n_tasks": row.get("n_tasks"),
                    "severity": "critical" if gate_val == 0 else "high",
                    "notes": row.get("notes") or f"{int((1 - gate_val) * 100)}% silent-zero rate observed",
                    "source": row.get("source_path"),
                }
            )
    warnings.sort(key=lambda w: (w["gate_pass_rate"], -(w["n_tasks"] or 0)))
    return {
        "_meta": {
            "public_release": True,
            "license": "CC-BY-4.0",
            "description": (
                "Workloads with observed gate-pass rate <= 50%. Save time — don't "
                "pay for these without fixing upstream first."
            ),
            "generated_from": "gpu_roi_table.json",
        },
        "warnings": warnings,
    }


def main():
    src_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("../../../gpu-fleet/lib").resolve()
    dst_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path(".").resolve()
    dst_dir.mkdir(parents=True, exist_ok=True)

    roi_src = src_dir / "gpu_roi_table.json"
    compat_src = src_dir / "workload_compatibility.json"
    picker_src = src_dir / "gpu_picker.py"

    roi = json.loads(roi_src.read_text())
    compat = json.loads(compat_src.read_text())

    roi_pub = sanitize_roi(roi)
    compat_pub = sanitize_compat(compat)
    silent = derive_silent_zero(roi_pub)

    (dst_dir / "gpu_roi_table.json").write_text(json.dumps(roi_pub, indent=2) + "\n")
    (dst_dir / "workload_compatibility.json").write_text(json.dumps(compat_pub, indent=2) + "\n")
    (dst_dir / "silent_zero_warnings.json").write_text(json.dumps(silent, indent=2) + "\n")

    # Copy gpu_picker.py verbatim — it's already clean logic
    (dst_dir / "gpu_picker.py").write_text(picker_src.read_text())

    print(f"[sanitize] wrote public JSONs to {dst_dir}")
    print(f"[sanitize]   rows:     {len(roi_pub.get('rows', []))}")
    print(f"[sanitize]   workloads:{len(compat_pub.get('workloads', {}))}")
    print(f"[sanitize]   warnings: {len(silent['warnings'])}")


if __name__ == "__main__":
    main()
