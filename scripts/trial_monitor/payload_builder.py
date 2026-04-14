#!/usr/bin/env python3
"""
payload_builder.py — Maps ClinicalTrials.gov v2 API schema to /api/v2/trials payload.

FIELD MAP (ClinicalTrials.gov → platform):
  protocolSection.identificationModule.nctId          → nct_id
  protocolSection.identificationModule.officialTitle  → title (fallback: briefTitle)
  protocolSection.identificationModule.briefTitle     → brief_title
  protocolSection.statusModule.overallStatus          → status  (normalized to lowercase)
  protocolSection.designModule.phases[]               → phase   (e.g. "PHASE3" → "Phase 3")
  protocolSection.conditionsModule.conditions[]       → conditions (JSON array string)
  protocolSection.interventionsModule.interventions[] → interventions (JSON array string)
  protocolSection.sponsorCollaboratorsModule          → sponsor
  protocolSection.designModule.enrollmentInfo.count   → enrollment
  protocolSection.statusModule.startDateStruct.date   → start_date
  protocolSection.statusModule.primaryCompletionDateStruct.date → primary_completion_date
  protocolSection.statusModule.lastUpdatePostDateStruct.date    → last_update_posted
  protocolSection.descriptionModule.briefSummary      → brief_summary
  protocolSection.eligibilityModule.eligibilityCriteria → eligibility_criteria
  protocolSection.contactsLocationsModule.locations[] → locations (JSON array string)
  resultsSection presence                             → has_results (bool)
  derivedSection.interventionBrowseModule.meshes[]    → mesh_terms (JSON array string)
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


_PHASE_MAP: Dict[str, str] = {
    "PHASE1": "Phase 1",
    "PHASE2": "Phase 2",
    "PHASE3": "Phase 3",
    "PHASE4": "Phase 4",
    "EARLY_PHASE1": "Early Phase 1",
    "NA": "N/A",
}

_STATUS_MAP: Dict[str, str] = {
    "RECRUITING": "recruiting",
    "ACTIVE_NOT_RECRUITING": "active_not_recruiting",
    "ENROLLING_BY_INVITATION": "enrolling_by_invitation",
    "COMPLETED": "completed",
    "TERMINATED": "terminated",
    "SUSPENDED": "suspended",
    "WITHDRAWN": "withdrawn",
    "NOT_YET_RECRUITING": "not_yet_recruiting",
    "UNKNOWN": "unknown",
}


def _safe_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    return str(val).strip() or None


def _norm_phase(phases: List[str]) -> str:
    """Normalise phase list to a human-readable string."""
    if not phases:
        return "N/A"
    mapped = [_PHASE_MAP.get(p, p) for p in phases]
    return "/".join(mapped)


def _norm_status(raw: Optional[str]) -> str:
    if not raw:
        return "unknown"
    return _STATUS_MAP.get(raw.upper(), raw.lower())


def _extract_sponsor(sponsor_module: Dict) -> Optional[str]:
    lead = sponsor_module.get("leadSponsor", {})
    return _safe_str(lead.get("name"))


def _extract_locations(locations: List[Dict]) -> str:
    """Return JSON-encoded list of {city, country} dicts."""
    result = []
    for loc in locations[:50]:  # cap at 50 to avoid huge payloads
        city = loc.get("city")
        country = loc.get("country")
        if city or country:
            result.append({"city": city, "country": country})
    return json.dumps(result)


def _extract_interventions(interventions: List[Dict]) -> str:
    """Return JSON-encoded list of {name, type} dicts."""
    result = []
    for iv in interventions:
        result.append({
            "name": iv.get("name"),
            "type": iv.get("type"),
        })
    return json.dumps(result)


def _extract_mesh_terms(derived: Dict) -> str:
    meshes = derived.get("interventionBrowseModule", {}).get("meshes", [])
    terms = [m.get("term") for m in meshes if m.get("term")]
    return json.dumps(terms)


def build_payload(study: Dict) -> Dict[str, Any]:
    """
    Convert a single ClinicalTrials.gov v2 study dict to the /api/v2/trials payload.

    Args:
        study: Raw study dict from ClinicalTrials.gov API response (one element of .studies[])

    Returns:
        Dict ready to POST or PATCH to /api/v2/trials
    """
    protocol = study.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status_mod = protocol.get("statusModule", {})
    design_mod = protocol.get("designModule", {})
    cond_mod = protocol.get("conditionsModule", {})
    intr_mod = protocol.get("interventionsModule", {})
    sponsor_mod = protocol.get("sponsorCollaboratorsModule", {})
    desc_mod = protocol.get("descriptionModule", {})
    elig_mod = protocol.get("eligibilityModule", {})
    contacts_mod = protocol.get("contactsLocationsModule", {})
    derived = study.get("derivedSection", {})
    results_section = study.get("resultsSection")

    nct_id = _safe_str(ident.get("nctId"))
    official_title = _safe_str(ident.get("officialTitle"))
    brief_title = _safe_str(ident.get("briefTitle"))
    title = official_title or brief_title

    raw_status = status_mod.get("overallStatus")
    status = _norm_status(raw_status)

    phases = design_mod.get("phases", [])
    phase = _norm_phase(phases)

    enrollment_info = design_mod.get("enrollmentInfo", {})
    enrollment = enrollment_info.get("count")

    start_date = _safe_str(
        (status_mod.get("startDateStruct") or {}).get("date")
    )
    primary_completion_date = _safe_str(
        (status_mod.get("primaryCompletionDateStruct") or {}).get("date")
    )
    last_update_posted = _safe_str(
        (status_mod.get("lastUpdatePostDateStruct") or {}).get("date")
    )

    conditions = json.dumps(cond_mod.get("conditions", []))
    interventions_list = intr_mod.get("interventions", [])
    interventions = _extract_interventions(interventions_list)

    sponsor = _extract_sponsor(sponsor_mod)
    brief_summary = _safe_str(desc_mod.get("briefSummary"))
    eligibility_criteria = _safe_str(elig_mod.get("eligibilityCriteria"))

    locations_list = contacts_mod.get("locations", [])
    locations = _extract_locations(locations_list)

    mesh_terms = _extract_mesh_terms(derived)
    has_results = results_section is not None

    payload: Dict[str, Any] = {
        "nct_id": nct_id,
        "title": title,
        "brief_title": brief_title,
        "status": status,
        "phase": phase,
        "conditions": conditions,
        "interventions": interventions,
        "sponsor": sponsor,
        "enrollment": enrollment,
        "start_date": start_date,
        "primary_completion_date": primary_completion_date,
        "last_update_posted": last_update_posted,
        "brief_summary": brief_summary,
        "eligibility_criteria": eligibility_criteria,
        "locations": locations,
        "mesh_terms": mesh_terms,
        "has_results": has_results,
    }

    # Remove None values — platform treats missing fields as unchanged on PATCH
    return {k: v for k, v in payload.items() if v is not None}


def is_significant_change(old: Dict, new_payload: Dict) -> bool:
    """
    Return True if the change warrants a Slack notification.
    Significant: new Phase 3 trial, results posted, or status flip to/from recruiting.
    """
    old_phase = (old.get("phase") or "").lower()
    new_phase = (new_payload.get("phase") or "").lower()
    if "phase 3" in new_phase and "phase 3" not in old_phase:
        return True

    old_has_results = old.get("has_results", False)
    new_has_results = new_payload.get("has_results", False)
    if new_has_results and not old_has_results:
        return True

    significant_statuses = {"recruiting", "active_not_recruiting", "completed", "terminated"}
    old_status = old.get("status", "")
    new_status = new_payload.get("status", "")
    if old_status != new_status and new_status in significant_statuses:
        return True

    return False
