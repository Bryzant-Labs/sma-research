"""Smoke tests for the /api/v2/infrastructure/* endpoints.

Run on the moltbot backend:
    cd /home/bryzant/sma-platform && source venv/bin/activate
    cd src && pytest -xvs ../tests/api/test_infrastructure.py

These tests exercise the DB-independent endpoints only — they do NOT touch
Postgres, they only verify JSON + picker logic.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sma_platform.api.app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_gpu_roi_table_returns_rows(client):
    r = client.get("/api/v2/infrastructure/gpu-roi")
    assert r.status_code == 200
    data = r.json()
    assert "rows" in data
    assert isinstance(data["rows"], list)
    assert len(data["rows"]) >= 10, "expect at least 10 public rows"
    # Cache header present
    cc = r.headers.get("Cache-Control", "")
    assert "max-age" in cc


def test_gpu_roi_is_clean_of_invoice_ids(client):
    """No 8-digit Vast invoice IDs should leak into the public JSON."""
    import re
    r = client.get("/api/v2/infrastructure/gpu-roi")
    body = r.text
    # 8-digit numbers starting with 3 (Vast invoice-ID shape)
    leaked = re.findall(r"\b3\d{7}\b", body)
    assert not leaked, f"Vast invoice IDs leaked: {leaked[:3]}"


def test_workload_compatibility(client):
    r = client.get("/api/v2/infrastructure/workload-compatibility")
    assert r.status_code == 200
    data = r.json()
    assert "workloads" in data
    assert len(data["workloads"]) >= 15
    assert "gpu_columns" in data
    assert len(data["gpu_columns"]) >= 8


def test_silent_zero_warnings(client):
    r = client.get("/api/v2/infrastructure/silent-zero")
    assert r.status_code == 200
    data = r.json()
    assert "warnings" in data
    # We expect at least molmim + rfdiffusion + mpnn
    workloads_flagged = {w["workload"] for w in data["warnings"]}
    assert any("molmim" in w for w in workloads_flagged), f"expected molmim flagged, got {workloads_flagged}"
    for w in data["warnings"]:
        assert 0 <= w["gate_pass_rate"] <= 0.5


def test_list_workloads(client):
    r = client.get("/api/v2/infrastructure/workloads")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == len(data["workloads"])
    # Union of compat + ROI should contain both the streaming ROI name
    # and the compat-side affinity name.
    assert "boltz2_rescore_streaming" in data["workloads"]
    assert "boltz2_affinity" in data["workloads"]
    # details map must flag provenance
    detail = {d["name"]: d for d in data["details"]}
    assert detail["boltz2_rescore_streaming"]["has_roi_rows"] is True
    assert detail["boltz2_affinity"]["in_compat_matrix"] is True


def test_pick_rank3(client):
    r = client.post(
        "/api/v2/infrastructure/pick",
        json={"workload": "boltz2_rescore_streaming", "problem_size": 300, "batch_size": 500},
    )
    assert r.status_code == 200
    data = r.json()
    assert "options" in data
    assert 1 <= len(data["options"]) <= 3
    for opt in data["options"]:
        assert "gpu" in opt
        assert "rationale" in opt
        assert "rank" in opt


def test_pick_prefers_free_when_available(client):
    r = client.post(
        "/api/v2/infrastructure/pick",
        json={"workload": "protein_mpnn", "prefer_free": True},
    )
    assert r.status_code == 200
    opt = r.json()["options"][0]
    assert opt["gpu"] == "hosted_NIM"
    assert opt["expected_usd_per_unit"] == 0.0


def test_pick_unknown_workload_returns_no_match(client):
    r = client.post(
        "/api/v2/infrastructure/pick",
        json={"workload": "totally_fake_workload_123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["options"][0]["gpu"] == "NO_MATCH"


def test_pick_validates_body(client):
    """Empty body should 422, not 500."""
    r = client.post("/api/v2/infrastructure/pick", json={})
    assert r.status_code == 422
