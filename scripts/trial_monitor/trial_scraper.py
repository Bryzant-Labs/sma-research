#!/usr/bin/env python3
"""
trial_scraper.py — Daily ClinicalTrials.gov scraper for SMA and IDH1 platforms.

Usage:
    python trial_scraper.py --topic sma --platform https://sma-research.info
    python trial_scraper.py --topic idh1 --platform https://idh1-research.info

Environment variables:
    SMA_PLATFORM_API_KEY     — API key for sma-research.info
    IDH1_PLATFORM_API_KEY    — API key for idh1-research.info
    SLACK_RESEARCH_WEBHOOK   — Slack webhook URL for significant-change alerts
                               (DM channel only — NEVER Tuvoc/Bryzant channels)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests
from dateutil import parser as dateutil_parser

from payload_builder import build_payload, is_significant_change

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CT_API_BASE = "https://clinicaltrials.gov/api/v2"
CT_PAGE_SIZE = 1000  # max allowed
CT_RATE_LIMIT_SLEEP = 1.2  # seconds between pages (~50 req/min limit)

ACTIVE_STATUSES = [
    "RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
]

# Include COMPLETED trials updated within past 90 days (results posted etc.)
COMPLETED_LOOKBACK_DAYS = 90

TOPIC_CONFIG: Dict[str, Dict[str, Any]] = {
    "sma": {
        "condition": "Spinal Muscular Atrophy",
        "api_key_env": "SMA_PLATFORM_API_KEY",
    },
    "idh1": {
        "condition": "IDH1 mutant OR isocitrate dehydrogenase 1",
        "api_key_env": "IDH1_PLATFORM_API_KEY",
    },
}


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _setup_logging(topic: str, log_dir: str) -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    today = date.today().isoformat()
    log_file = os.path.join(log_dir, f"trial_scraper_{topic}_{today}.log")

    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger = logging.getLogger(f"trial_scraper.{topic}")
    logger.info("Log file: %s", log_file)
    return logger


# ---------------------------------------------------------------------------
# HTTP helpers with retry
# ---------------------------------------------------------------------------

def _get_with_retry(
    url: str,
    params: Dict,
    logger: logging.Logger,
    max_retries: int = 5,
    timeout: int = 30,
) -> requests.Response:
    """GET with exponential backoff on 429/503."""
    delay = 2.0
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code in (429, 503):
                wait = delay * (2 ** (attempt - 1))
                logger.warning(
                    "HTTP %d on attempt %d/%d — sleeping %.1fs",
                    resp.status_code, attempt, max_retries, wait,
                )
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            if attempt == max_retries:
                raise
            wait = delay * (2 ** (attempt - 1))
            logger.warning("Request error attempt %d/%d: %s — retry in %.1fs", attempt, max_retries, exc, wait)
            time.sleep(wait)
    raise RuntimeError(f"Failed after {max_retries} retries: {url}")


def _platform_request(
    method: str,
    url: str,
    api_key: str,
    logger: logging.Logger,
    json_body: Optional[Dict] = None,
    params: Optional[Dict] = None,
    max_retries: int = 3,
) -> Optional[requests.Response]:
    """Wrapper for platform API calls with retry on 429/503."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    delay = 2.0
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                json=json_body,
                params=params,
                timeout=30,
            )
            if resp.status_code in (429, 503):
                wait = delay * (2 ** (attempt - 1))
                logger.warning("Platform HTTP %d attempt %d — sleep %.1fs", resp.status_code, attempt, wait)
                time.sleep(wait)
                continue
            return resp
        except requests.RequestException as exc:
            if attempt == max_retries:
                logger.error("Platform request failed after %d retries: %s", max_retries, exc)
                return None
            time.sleep(delay * (2 ** (attempt - 1)))
    return None


# ---------------------------------------------------------------------------
# ClinicalTrials.gov fetching
# ---------------------------------------------------------------------------

def _fetch_ct_page(
    condition: str,
    status_filter: str,
    page_token: Optional[str],
    logger: logging.Logger,
) -> Tuple[List[Dict], Optional[str], int]:
    """Fetch one page from ClinicalTrials.gov. Returns (studies, next_page_token, total_count)."""
    params: Dict[str, Any] = {
        "query.cond": condition,
        "filter.overallStatus": status_filter,
        "sort": "LastUpdatePostDate:desc",
        "pageSize": CT_PAGE_SIZE,
        "format": "json",
    }
    if page_token:
        params["pageToken"] = page_token

    url = f"{CT_API_BASE}/studies"
    resp = _get_with_retry(url, params, logger)
    data = resp.json()

    studies = data.get("studies", [])
    next_token = data.get("nextPageToken")
    total = data.get("totalCount", 0)
    return studies, next_token, total


def fetch_all_trials(
    condition: str,
    logger: logging.Logger,
) -> List[Dict]:
    """
    Paginate through all matching trials from ClinicalTrials.gov.
    Combines active statuses + recent completed (90-day window).
    """
    all_studies: List[Dict] = []
    cutoff = date.today() - timedelta(days=COMPLETED_LOOKBACK_DAYS)

    # Pass 1: active statuses
    active_filter = ",".join(ACTIVE_STATUSES)
    page_token: Optional[str] = None
    page_num = 0

    while True:
        studies, page_token, total = _fetch_ct_page(condition, active_filter, page_token, logger)
        page_num += 1
        all_studies.extend(studies)
        logger.info("CT active page %d — %d studies (total reported: %d)", page_num, len(studies), total)

        if not page_token:
            break
        time.sleep(CT_RATE_LIMIT_SLEEP)

    # Pass 2: completed — filter by last_update_posted >= cutoff
    page_token = None
    page_num = 0
    while True:
        studies, page_token, total = _fetch_ct_page(condition, "COMPLETED", page_token, logger)
        page_num += 1
        recent = []
        for s in studies:
            status_mod = s.get("protocolSection", {}).get("statusModule", {})
            last_updated_raw = (status_mod.get("lastUpdatePostDateStruct") or {}).get("date")
            if last_updated_raw:
                try:
                    last_updated = dateutil_parser.parse(last_updated_raw).date()
                    if last_updated >= cutoff:
                        recent.append(s)
                except (ValueError, TypeError):
                    pass  # skip unparseable dates

        all_studies.extend(recent)
        logger.info(
            "CT completed page %d — %d in window of %d (total: %d)",
            page_num, len(recent), len(studies), total,
        )

        # If the page had no recent studies and we've paginated past the cutoff,
        # stop early (results are sorted by LastUpdatePostDate:desc)
        if len(recent) == 0 and len(studies) > 0:
            logger.info("No more recently-updated completed trials — stopping pagination")
            break

        if not page_token:
            break
        time.sleep(CT_RATE_LIMIT_SLEEP)

    # Deduplicate by NCT ID (active pass might overlap with completed in rare edge cases)
    seen: set = set()
    deduped = []
    for s in all_studies:
        nct = s.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
        if nct and nct not in seen:
            seen.add(nct)
            deduped.append(s)

    logger.info("Total fetched (deduped): %d trials", len(deduped))
    return deduped


# ---------------------------------------------------------------------------
# Platform API interactions
# ---------------------------------------------------------------------------

def check_trial_exists(
    platform_base: str,
    nct_id: str,
    api_key: str,
    logger: logging.Logger,
) -> Optional[Dict]:
    """
    GET /api/v2/trials?nct_id=<nct_id>
    Returns existing trial dict if found, None if not found or on error.
    """
    url = f"{platform_base}/api/v2/trials"
    resp = _platform_request("GET", url, api_key, logger, params={"nct_id": nct_id})
    if resp is None:
        return None
    if resp.status_code == 404:
        return None
    if resp.status_code == 200:
        data = resp.json()
        # Platform may return list or single object
        if isinstance(data, list):
            return data[0] if data else None
        return data if data else None
    logger.warning("Unexpected status %d checking %s", resp.status_code, nct_id)
    return None


def create_trial(
    platform_base: str,
    payload: Dict,
    api_key: str,
    logger: logging.Logger,
) -> bool:
    """POST /api/v2/trials — returns True on success."""
    url = f"{platform_base}/api/v2/trials"
    resp = _platform_request("POST", url, api_key, logger, json_body=payload)
    if resp is None:
        return False
    if resp.status_code in (200, 201):
        return True
    logger.error("POST %s failed: %d — %s", payload.get("nct_id"), resp.status_code, resp.text[:200])
    return False


def update_trial(
    platform_base: str,
    nct_id: str,
    payload: Dict,
    api_key: str,
    logger: logging.Logger,
) -> bool:
    """PATCH /api/v2/trials/<nct_id> — returns True on success."""
    url = f"{platform_base}/api/v2/trials/{nct_id}"
    resp = _platform_request("PATCH", url, api_key, logger, json_body=payload)
    if resp is None:
        return False
    if resp.status_code in (200, 204):
        return True
    logger.error("PATCH %s failed: %d — %s", nct_id, resp.status_code, resp.text[:200])
    return False


# ---------------------------------------------------------------------------
# Slack notification
# ---------------------------------------------------------------------------

def _send_slack_alert(
    topic: str,
    platform_base: str,
    nct_id: str,
    payload: Dict,
    reason: str,
    logger: logging.Logger,
) -> None:
    """
    POST a notification to SLACK_RESEARCH_WEBHOOK.
    NEVER posts to Bryzant/Tuvoc channels — research-only.
    """
    webhook = os.environ.get("SLACK_RESEARCH_WEBHOOK")
    if not webhook:
        logger.debug("SLACK_RESEARCH_WEBHOOK not set — skipping notification for %s", nct_id)
        return

    title = (payload.get("title") or "Unknown title")[:100]
    phase = payload.get("phase", "?")
    status = payload.get("status", "?")

    message = {
        "text": (
            f"*[{topic.upper()} Trial Monitor]* Significant change detected\n"
            f"*{nct_id}* — {title}\n"
            f"Phase: {phase} | Status: {status}\n"
            f"Reason: {reason}\n"
            f"Platform: {platform_base}/trials/{nct_id}"
        )
    }

    try:
        resp = requests.post(webhook, json=message, timeout=10)
        if resp.status_code != 200:
            logger.warning("Slack webhook returned %d: %s", resp.status_code, resp.text[:100])
        else:
            logger.info("Slack alert sent for %s (%s)", nct_id, reason)
    except requests.RequestException as exc:
        logger.warning("Slack notification failed for %s: %s", nct_id, exc)


# ---------------------------------------------------------------------------
# Core sync loop
# ---------------------------------------------------------------------------

def _dates_equal(date_a: Optional[str], date_b: Optional[str]) -> bool:
    """Compare two ISO date strings, ignoring time component."""
    if date_a is None and date_b is None:
        return True
    if date_a is None or date_b is None:
        return False
    try:
        return (
            dateutil_parser.parse(date_a).date()
            == dateutil_parser.parse(date_b).date()
        )
    except (ValueError, TypeError):
        return date_a == date_b


def sync_trials(
    studies: List[Dict],
    platform_base: str,
    api_key: str,
    topic: str,
    logger: logging.Logger,
) -> Dict[str, int]:
    """
    For each study: check existence, compare last_update_posted, create/update/skip.

    Returns stats dict: {new, updated, skipped, errors}.
    """
    stats = {"new": 0, "updated": 0, "skipped": 0, "errors": 0}
    total = len(studies)

    for idx, study in enumerate(studies, 1):
        try:
            payload = build_payload(study)
        except Exception as exc:
            logger.error("build_payload failed for study #%d: %s", idx, exc, exc_info=True)
            stats["errors"] += 1
            continue

        nct_id = payload.get("nct_id")
        if not nct_id:
            logger.warning("Study #%d has no NCT ID — skipping", idx)
            stats["errors"] += 1
            continue

        if idx % 50 == 0 or idx == total:
            logger.info("Progress: %d/%d (new=%d updated=%d skipped=%d errors=%d)",
                        idx, total, stats["new"], stats["updated"], stats["skipped"], stats["errors"])

        existing = check_trial_exists(platform_base, nct_id, api_key, logger)

        if existing is None:
            # New trial
            ok = create_trial(platform_base, payload, api_key, logger)
            if ok:
                stats["new"] += 1
                logger.debug("CREATED %s", nct_id)
                # New Phase 3 trial is a significant event
                if "phase 3" in (payload.get("phase") or "").lower():
                    _send_slack_alert(topic, platform_base, nct_id, payload, "New Phase 3 trial", logger)
            else:
                stats["errors"] += 1
        else:
            existing_date = existing.get("last_update_posted")
            new_date = payload.get("last_update_posted")

            if _dates_equal(existing_date, new_date):
                stats["skipped"] += 1
                logger.debug("SKIPPED %s (unchanged, last_update=%s)", nct_id, existing_date)
            else:
                significant = is_significant_change(existing, payload)
                ok = update_trial(platform_base, nct_id, payload, api_key, logger)
                if ok:
                    stats["updated"] += 1
                    logger.debug("UPDATED %s (%s → %s)", nct_id, existing_date, new_date)
                    if significant:
                        reason = _build_change_reason(existing, payload)
                        _send_slack_alert(topic, platform_base, nct_id, payload, reason, logger)
                else:
                    stats["errors"] += 1

    return stats


def _build_change_reason(old: Dict, new: Dict) -> str:
    parts = []
    if old.get("status") != new.get("status"):
        parts.append(f"status {old.get('status')} → {new.get('status')}")
    if not old.get("has_results") and new.get("has_results"):
        parts.append("results posted")
    if "phase 3" in (new.get("phase") or "").lower() and "phase 3" not in (old.get("phase") or "").lower():
        parts.append("upgraded to Phase 3")
    return "; ".join(parts) if parts else "data updated"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Daily ClinicalTrials.gov scraper")
    parser.add_argument(
        "--topic",
        required=True,
        choices=list(TOPIC_CONFIG.keys()),
        help="Topic to scrape: sma or idh1",
    )
    parser.add_argument(
        "--platform",
        required=True,
        help="Platform base URL, e.g. https://sma-research.info",
    )
    parser.add_argument(
        "--log-dir",
        default=os.path.expanduser("~/sma-research/logs"),
        help="Directory for log files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch from CT.gov and build payloads, but do not POST/PATCH to platform",
    )
    args = parser.parse_args()

    topic = args.topic
    platform_base = args.platform.rstrip("/")
    cfg = TOPIC_CONFIG[topic]

    logger = _setup_logging(topic, args.log_dir)
    logger.info("=== trial_scraper START topic=%s platform=%s dry_run=%s ===", topic, platform_base, args.dry_run)

    api_key_env = cfg["api_key_env"]
    api_key = os.environ.get(api_key_env, "")
    if not api_key and not args.dry_run:
        logger.error("Missing env var %s — cannot authenticate to platform", api_key_env)
        sys.exit(1)

    condition = cfg["condition"]
    logger.info("Fetching trials from ClinicalTrials.gov for condition: %r", condition)

    start_time = time.monotonic()
    try:
        studies = fetch_all_trials(condition, logger)
    except Exception as exc:
        logger.error("Fatal error fetching trials: %s", exc, exc_info=True)
        sys.exit(1)

    if args.dry_run:
        logger.info("DRY RUN — %d trials fetched, no platform writes", len(studies))
        for s in studies[:5]:
            try:
                payload = build_payload(s)
                logger.info("Sample payload: %s", json.dumps(payload, indent=2)[:300])
            except Exception as exc:
                logger.warning("Payload build error: %s", exc)
        return

    stats = sync_trials(studies, platform_base, api_key, topic, logger)

    elapsed = time.monotonic() - start_time
    logger.info(
        "=== DONE in %.1fs | new=%d updated=%d skipped=%d errors=%d ===",
        elapsed, stats["new"], stats["updated"], stats["skipped"], stats["errors"],
    )

    if stats["errors"] > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
