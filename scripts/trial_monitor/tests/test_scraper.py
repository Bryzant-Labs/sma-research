#!/usr/bin/env python3
"""
test_scraper.py — Unit tests for trial_scraper and payload_builder.

Run with:
    cd ~/sma-research/scripts/trial_monitor
    python -m pytest tests/test_scraper.py -v
"""

import json
import sys
import os
import time
import unittest
from datetime import date, timedelta
from typing import Any, Dict
from unittest.mock import MagicMock, patch, call

# Make parent directory importable without installing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from payload_builder import build_payload, is_significant_change
import trial_scraper


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_ct_study(
    nct_id: str = "NCT12345678",
    title: str = "Test SMA Trial",
    status: str = "RECRUITING",
    phases: list = None,
    last_update: str = "2026-04-10",
    has_results: bool = False,
) -> Dict[str, Any]:
    """Build a minimal ClinicalTrials.gov v2 study dict."""
    if phases is None:
        phases = ["PHASE3"]
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "officialTitle": title,
                "briefTitle": f"Brief: {title}",
            },
            "statusModule": {
                "overallStatus": status,
                "lastUpdatePostDateStruct": {"date": last_update},
                "startDateStruct": {"date": "2023-01-01"},
                "primaryCompletionDateStruct": {"date": "2025-12-31"},
            },
            "designModule": {
                "phases": phases,
                "enrollmentInfo": {"count": 150},
            },
            "conditionsModule": {
                "conditions": ["Spinal Muscular Atrophy"],
            },
            "interventionsModule": {
                "interventions": [
                    {"name": "Risdiplam", "type": "DRUG"},
                ],
            },
            "sponsorCollaboratorsModule": {
                "leadSponsor": {"name": "Hoffmann-La Roche"},
            },
            "descriptionModule": {
                "briefSummary": "A trial summary.",
            },
            "eligibilityModule": {
                "eligibilityCriteria": "Inclusion: SMA diagnosis.",
            },
            "contactsLocationsModule": {
                "locations": [
                    {"city": "Berlin", "country": "Germany"},
                    {"city": "London", "country": "UK"},
                ],
            },
        },
        "derivedSection": {
            "interventionBrowseModule": {
                "meshes": [{"term": "Risdiplam"}],
            },
        },
        "resultsSection": {"some": "results"} if has_results else None,
    }


def _make_platform_trial(
    nct_id: str = "NCT12345678",
    phase: str = "Phase 3",
    status: str = "recruiting",
    last_update_posted: str = "2026-04-10",
    has_results: bool = False,
) -> Dict[str, Any]:
    return {
        "nct_id": nct_id,
        "phase": phase,
        "status": status,
        "last_update_posted": last_update_posted,
        "has_results": has_results,
    }


# ---------------------------------------------------------------------------
# Tests: payload_builder
# ---------------------------------------------------------------------------

class TestPayloadBuilder(unittest.TestCase):

    def test_basic_field_mapping(self):
        study = _make_ct_study()
        payload = build_payload(study)

        self.assertEqual(payload["nct_id"], "NCT12345678")
        self.assertEqual(payload["title"], "Test SMA Trial")
        self.assertEqual(payload["status"], "recruiting")
        self.assertEqual(payload["phase"], "Phase 3")
        self.assertEqual(payload["enrollment"], 150)
        self.assertEqual(payload["last_update_posted"], "2026-04-10")
        self.assertFalse(payload["has_results"])

    def test_title_fallback_to_brief(self):
        study = _make_ct_study()
        # Remove officialTitle
        del study["protocolSection"]["identificationModule"]["officialTitle"]
        payload = build_payload(study)
        self.assertEqual(payload["title"], "Brief: Test SMA Trial")

    def test_phase_normalisation(self):
        cases = [
            (["PHASE1"], "Phase 1"),
            (["PHASE2"], "Phase 2"),
            (["PHASE3"], "Phase 3"),
            (["EARLY_PHASE1"], "Early Phase 1"),
            ([], "N/A"),
            (["PHASE1", "PHASE2"], "Phase 1/Phase 2"),
        ]
        for phases, expected in cases:
            study = _make_ct_study(phases=phases)
            payload = build_payload(study)
            self.assertEqual(payload["phase"], expected, f"Failed for phases={phases}")

    def test_status_normalisation(self):
        cases = [
            ("RECRUITING", "recruiting"),
            ("ACTIVE_NOT_RECRUITING", "active_not_recruiting"),
            ("COMPLETED", "completed"),
            ("TERMINATED", "terminated"),
        ]
        for raw, expected in cases:
            study = _make_ct_study(status=raw)
            payload = build_payload(study)
            self.assertEqual(payload["status"], expected)

    def test_conditions_serialised_as_json(self):
        study = _make_ct_study()
        payload = build_payload(study)
        conditions = json.loads(payload["conditions"])
        self.assertIn("Spinal Muscular Atrophy", conditions)

    def test_interventions_serialised_as_json(self):
        study = _make_ct_study()
        payload = build_payload(study)
        interventions = json.loads(payload["interventions"])
        self.assertEqual(len(interventions), 1)
        self.assertEqual(interventions[0]["name"], "Risdiplam")

    def test_locations_capped_at_50(self):
        study = _make_ct_study()
        study["protocolSection"]["contactsLocationsModule"]["locations"] = [
            {"city": f"City{i}", "country": "XX"} for i in range(100)
        ]
        payload = build_payload(study)
        locs = json.loads(payload["locations"])
        self.assertEqual(len(locs), 50)

    def test_has_results_true(self):
        study = _make_ct_study(has_results=True)
        payload = build_payload(study)
        self.assertTrue(payload["has_results"])

    def test_none_values_excluded(self):
        study = _make_ct_study()
        # Remove optional fields
        del study["protocolSection"]["descriptionModule"]
        payload = build_payload(study)
        self.assertNotIn("brief_summary", payload)

    def test_mesh_terms_serialised(self):
        study = _make_ct_study()
        payload = build_payload(study)
        terms = json.loads(payload["mesh_terms"])
        self.assertIn("Risdiplam", terms)


# ---------------------------------------------------------------------------
# Tests: is_significant_change
# ---------------------------------------------------------------------------

class TestSignificantChange(unittest.TestCase):

    def test_new_phase3(self):
        old = _make_platform_trial(phase="Phase 2")
        new = build_payload(_make_ct_study(phases=["PHASE3"]))
        self.assertTrue(is_significant_change(old, new))

    def test_phase3_to_phase3_not_significant(self):
        old = _make_platform_trial(phase="Phase 3")
        new = build_payload(_make_ct_study(phases=["PHASE3"]))
        self.assertFalse(is_significant_change(old, new))

    def test_results_posted(self):
        old = _make_platform_trial(has_results=False)
        new = build_payload(_make_ct_study(has_results=True))
        self.assertTrue(is_significant_change(old, new))

    def test_status_flip_to_recruiting(self):
        old = _make_platform_trial(status="not_yet_recruiting")
        new = build_payload(_make_ct_study(status="RECRUITING"))
        self.assertTrue(is_significant_change(old, new))

    def test_status_flip_to_completed(self):
        old = _make_platform_trial(status="active_not_recruiting")
        new = build_payload(_make_ct_study(status="COMPLETED"))
        self.assertTrue(is_significant_change(old, new))

    def test_minor_update_not_significant(self):
        old = _make_platform_trial(phase="Phase 2", status="recruiting")
        new = build_payload(_make_ct_study(phases=["PHASE2"], status="RECRUITING"))
        self.assertFalse(is_significant_change(old, new))


# ---------------------------------------------------------------------------
# Tests: new vs update vs skip logic
# ---------------------------------------------------------------------------

class TestSyncLogic(unittest.TestCase):

    def _run_sync(self, existing_trial, study):
        """Helper: run sync_trials with mocked platform calls."""
        logger = MagicMock()

        with patch("trial_scraper.check_trial_exists") as mock_check, \
             patch("trial_scraper.create_trial") as mock_create, \
             patch("trial_scraper.update_trial") as mock_update, \
             patch("trial_scraper._send_slack_alert") as mock_slack:

            mock_check.return_value = existing_trial
            mock_create.return_value = True
            mock_update.return_value = True

            stats = trial_scraper.sync_trials(
                [study],
                platform_base="https://sma-research.info",
                api_key="test-key",
                topic="sma",
                logger=logger,
            )

        return stats, mock_create, mock_update, mock_slack

    def test_new_trial_is_posted(self):
        study = _make_ct_study(nct_id="NCT00000001")
        stats, mock_create, mock_update, _ = self._run_sync(None, study)
        mock_create.assert_called_once()
        mock_update.assert_not_called()
        self.assertEqual(stats["new"], 1)
        self.assertEqual(stats["updated"], 0)
        self.assertEqual(stats["skipped"], 0)

    def test_unchanged_trial_is_skipped(self):
        existing = _make_platform_trial(nct_id="NCT00000002", last_update_posted="2026-04-10")
        study = _make_ct_study(nct_id="NCT00000002", last_update="2026-04-10")
        stats, mock_create, mock_update, _ = self._run_sync(existing, study)
        mock_create.assert_not_called()
        mock_update.assert_not_called()
        self.assertEqual(stats["skipped"], 1)

    def test_updated_trial_is_patched(self):
        existing = _make_platform_trial(nct_id="NCT00000003", last_update_posted="2026-04-01")
        study = _make_ct_study(nct_id="NCT00000003", last_update="2026-04-10")
        stats, mock_create, mock_update, _ = self._run_sync(existing, study)
        mock_create.assert_not_called()
        mock_update.assert_called_once()
        self.assertEqual(stats["updated"], 1)

    def test_slack_fired_on_phase3_flip(self):
        existing = _make_platform_trial(nct_id="NCT00000004", phase="Phase 2", last_update_posted="2026-04-01")
        study = _make_ct_study(nct_id="NCT00000004", phases=["PHASE3"], last_update="2026-04-10")
        _, _, _, mock_slack = self._run_sync(existing, study)
        mock_slack.assert_called_once()
        call_args = mock_slack.call_args[0]
        self.assertIn("NCT00000004", call_args)

    def test_slack_fired_on_new_phase3(self):
        study = _make_ct_study(nct_id="NCT00000005", phases=["PHASE3"])
        _, mock_create, _, mock_slack = self._run_sync(None, study)
        mock_create.assert_called_once()
        mock_slack.assert_called_once()
        call_args = mock_slack.call_args[0]
        self.assertIn("New Phase 3 trial", call_args)

    def test_no_slack_for_minor_update(self):
        existing = _make_platform_trial(nct_id="NCT00000006", phase="Phase 2", status="recruiting",
                                         last_update_posted="2026-04-01")
        study = _make_ct_study(nct_id="NCT00000006", phases=["PHASE2"], status="RECRUITING",
                                last_update="2026-04-10")
        _, _, mock_update, mock_slack = self._run_sync(existing, study)
        mock_update.assert_called_once()
        mock_slack.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: pagination handling
# ---------------------------------------------------------------------------

class TestPagination(unittest.TestCase):

    def test_paginate_active_trials(self):
        """Verify fetch_all_trials follows nextPageToken until exhausted."""
        logger = MagicMock()

        page1_studies = [_make_ct_study(nct_id=f"NCT{i:08d}") for i in range(3)]
        page2_studies = [_make_ct_study(nct_id=f"NCT{i:08d}") for i in range(3, 5)]

        call_count = {"n": 0}

        def fake_fetch(condition, status_filter, page_token, log):
            call_count["n"] += 1
            if "COMPLETED" in status_filter:
                return [], None, 0
            if page_token is None:
                return page1_studies, "TOKEN_2", len(page1_studies) + len(page2_studies)
            else:
                return page2_studies, None, len(page1_studies) + len(page2_studies)

        with patch("trial_scraper._fetch_ct_page", side_effect=fake_fetch), \
             patch("trial_scraper.time.sleep"):
            results = trial_scraper.fetch_all_trials("Spinal Muscular Atrophy", logger)

        self.assertEqual(len(results), 5)
        nct_ids = [r["protocolSection"]["identificationModule"]["nctId"] for r in results]
        for i in range(5):
            self.assertIn(f"NCT{i:08d}", nct_ids)

    def test_completed_trials_filtered_by_date(self):
        """Only recently-updated completed trials should be included."""
        logger = MagicMock()
        recent_date = (date.today() - timedelta(days=10)).isoformat()
        old_date = (date.today() - timedelta(days=120)).isoformat()

        recent_study = _make_ct_study(nct_id="NCT00000100", status="COMPLETED", last_update=recent_date)
        old_study = _make_ct_study(nct_id="NCT00000101", status="COMPLETED", last_update=old_date)

        def fake_fetch(condition, status_filter, page_token, log):
            if "COMPLETED" in status_filter:
                return [recent_study, old_study], None, 2
            return [], None, 0

        with patch("trial_scraper._fetch_ct_page", side_effect=fake_fetch), \
             patch("trial_scraper.time.sleep"):
            results = trial_scraper.fetch_all_trials("Spinal Muscular Atrophy", logger)

        nct_ids = [r["protocolSection"]["identificationModule"]["nctId"] for r in results]
        self.assertIn("NCT00000100", nct_ids)
        self.assertNotIn("NCT00000101", nct_ids)


# ---------------------------------------------------------------------------
# Tests: HTTP retry on 429/503
# ---------------------------------------------------------------------------

class TestHttpRetry(unittest.TestCase):

    def test_retries_on_429(self):
        """GET should retry on 429 and succeed on third attempt."""
        logger = MagicMock()

        responses = [
            MagicMock(status_code=429, raise_for_status=lambda: None),
            MagicMock(status_code=429, raise_for_status=lambda: None),
            MagicMock(status_code=200, raise_for_status=lambda: None, json=lambda: {"studies": [], "totalCount": 0}),
        ]

        with patch("trial_scraper.requests.get", side_effect=responses), \
             patch("trial_scraper.time.sleep"):
            resp = trial_scraper._get_with_retry(
                "https://clinicaltrials.gov/api/v2/studies",
                {},
                logger,
                max_retries=5,
            )

        self.assertEqual(resp.status_code, 200)

    def test_raises_after_max_retries(self):
        """Should raise RuntimeError after exhausting retries."""
        logger = MagicMock()

        always_429 = MagicMock(status_code=429, raise_for_status=lambda: None)

        with patch("trial_scraper.requests.get", return_value=always_429), \
             patch("trial_scraper.time.sleep"):
            with self.assertRaises(RuntimeError):
                trial_scraper._get_with_retry(
                    "https://clinicaltrials.gov/api/v2/studies",
                    {},
                    logger,
                    max_retries=3,
                )

    def test_retries_on_503(self):
        """Platform request should retry on 503."""
        logger = MagicMock()

        responses = [
            MagicMock(status_code=503),
            MagicMock(status_code=200),
        ]

        with patch("trial_scraper.requests.request", side_effect=responses), \
             patch("trial_scraper.time.sleep"):
            resp = trial_scraper._platform_request(
                "GET",
                "https://sma-research.info/api/v2/trials",
                "test-key",
                logger,
                max_retries=3,
            )

        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
