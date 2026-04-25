#!/usr/bin/env python3
"""
lincs_matcher.py — LINCS L1000 connectivity / signature-matching tool

Matches a disease (up/down) gene signature against the LINCS L1000 perturbation
database and returns drugs whose perturbation REVERSES the disease signature
(classic Connectivity Map approach, Lamb 2006).

Primary engine: L1000CDS^2 REST API (Ma'ayan Lab, Duan 2016 NPJ Syst Biol Appl)
    - Free, no API key, no install
    - Searches ~30k drug/tool-compound L1000 signatures across 9 cell lines
    - Returns CMap-style overlap score, pert_id, pert_iname (drug), cell_line,
      dose, pubchem_id
    - aggravate=false  -> REVERSERS (therapeutic hits)
    - aggravate=true   -> MIMICS (disease-matching; useful as negative control)

Fallback engine: SigCom LINCS API (Evangelista 2022) — optional, disabled by default.

Signature input TSV columns (tab-separated, header required):
    gene    direction
    ROCK2   DOWN
    TP53    UP
    ...
Alternate accepted columns: {gene_symbol, symbol} and {dir, sign} (+1/-1).

Usage:
    lincs_matcher.py --signature <query.tsv> --output <hits.tsv> \\
        [--top-n 30] [--cell-line-filter neuronal|all] \\
        [--direction reverse|mimic] [--max-genes 150]

Output columns:
    pert_id, pert_iname, cell_line, dose, dose_unit,
    connectivity_score, fdr, n_genes_overlapped, direction, pubchem_id, sig_id

Constraints: CPU only, no large downloads, <30 min, Python 3.9+ stdlib + requests.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    import urllib.request
    import urllib.error
except Exception as e:  # pragma: no cover
    print(f"stdlib urllib missing: {e}", file=sys.stderr)
    sys.exit(2)

# -----------------------------------------------------------------------------#
# Config                                                                        #
# -----------------------------------------------------------------------------#
L1000CDS2_URL = "https://maayanlab.cloud/L1000CDS2/query"
# Known L1000 neuronal-lineage cell lines in clue.io Touchstone + Core:
#   NEU         = primary-like neuron model (iPSC-neuron, limited coverage)
#   SHSY5Y      = SH-SY5Y neuroblastoma
#   SH-SY5Y     = alt spelling
#   NPC         = neural progenitor cell
#   U251MG      = glioblastoma
#   U87MG       = glioblastoma
#   SKNSH       = SK-N-SH neuroblastoma
#   MCF10A      = mammary epithelial (NOT neural — excluded)
# We also accept any id starting with "NEU" or containing "NEURO"/"GLI" safely.
NEURONAL_CELL_IDS = {
    # From GSE92742 cell_info.txt (verified 2026-04-20):
    "NEU", "NEU.KCL", "MNEU", "MNEU.E", "NPC", "NPC.CAS9", "NPC.TAK", "FIBRNPC",
    "SHSY5Y", "SH-SY5Y", "SKNSH", "SK-N-SH",
    "U251MG", "U87MG", "U-87MG",
    "GBM", "NEURO",
}
NEURONAL_PREFIX = ("NEU", "MNEU", "NPC", "SHSY", "SKN", "U87", "U251", "FIBRNPC")

TIMEOUT_S = 60
MAX_RETRIES = 3
RETRY_BACKOFF_S = 5


# -----------------------------------------------------------------------------#
# Signature handling                                                            #
# -----------------------------------------------------------------------------#
def parse_signature(path: Path, max_genes: int = 150) -> tuple[list[str], list[str]]:
    """Load a TSV signature and split into UP and DOWN gene lists.

    Accepts:
        gene<TAB>direction                 where direction in {UP,DOWN,+1,-1,1,-1}
        gene_symbol<TAB>log2FC             (DOWN if <0, UP if >0)
        gene<TAB>sign                      (numeric)
        gene<TAB>direction<TAB>log2FC      (rank by |log2FC| if present)

    Returns (up_genes, down_genes), each capped at max_genes and in
    |effect|-descending order if log2FC is available.
    """
    with path.open() as fh:
        header = fh.readline().rstrip("\n").split("\t")
        hdr = [h.strip().lower() for h in header]

    # Identify columns
    def find(*names):
        for n in names:
            if n in hdr:
                return hdr.index(n)
        return None

    gene_col = find("gene", "gene_symbol", "symbol", "name", "gene_name")
    dir_col = find("direction", "dir", "sign")
    lfc_col = find("log2fc", "log2foldchange", "lfc", "effect", "meta_log2fc")

    if gene_col is None:
        raise ValueError(f"Signature file {path} missing gene column. Header: {header}")
    if dir_col is None and lfc_col is None:
        raise ValueError(
            f"Signature {path} needs a 'direction' (UP/DOWN) or 'log2FC' column. Header: {header}"
        )

    rows = []
    with path.open() as fh:
        fh.readline()  # skip header
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= max(c for c in (gene_col, dir_col, lfc_col) if c is not None):
                continue
            g = parts[gene_col].strip().upper()
            if not g or g in {"NA", "NAN", "-"}:
                continue
            lfc: Optional[float] = None
            if lfc_col is not None:
                try:
                    lfc = float(parts[lfc_col])
                except Exception:
                    lfc = None
            direction: Optional[str] = None
            if dir_col is not None:
                d = parts[dir_col].strip().upper()
                if d in {"UP", "+1", "1", "POS", "POSITIVE"}:
                    direction = "UP"
                elif d in {"DOWN", "-1", "NEG", "NEGATIVE"}:
                    direction = "DOWN"
            if direction is None and lfc is not None:
                direction = "UP" if lfc > 0 else "DOWN"
            if direction is None:
                continue
            rows.append((g, direction, lfc if lfc is not None else 0.0))

    # Dedup preserving max |lfc|
    best: Dict[str, tuple[str, float]] = {}
    for g, d, lfc in rows:
        if g not in best or abs(lfc) > abs(best[g][1]):
            best[g] = (d, lfc)

    up = [(g, lfc) for g, (d, lfc) in best.items() if d == "UP"]
    dn = [(g, lfc) for g, (d, lfc) in best.items() if d == "DOWN"]
    # Sort by |lfc| desc, cap
    up.sort(key=lambda x: -abs(x[1]))
    dn.sort(key=lambda x: -abs(x[1]))
    up_genes = [g for g, _ in up[:max_genes]]
    dn_genes = [g for g, _ in dn[:max_genes]]
    return up_genes, dn_genes


# -----------------------------------------------------------------------------#
# L1000CDS^2 query                                                              #
# -----------------------------------------------------------------------------#
def query_l1000cds2(up_genes: list[str], down_genes: list[str],
                    aggravate: bool = False) -> dict:
    """Query Ma'ayan Lab L1000CDS^2 REST API.

    aggravate=False -> return REVERSERS (drug perturbation opposite of disease)
    aggravate=True  -> return MIMICS (same direction as disease)
    """
    if not up_genes and not down_genes:
        raise ValueError("Signature has no UP and no DOWN genes.")
    payload = {
        "data": {
            "upGenes": list(up_genes),
            "dnGenes": list(down_genes),
        },
        "config": {
            "aggravate": bool(aggravate),
            "searchMethod": "geneSet",
            "share": False,
            "combination": False,
            "db-version": "latest",
        },
    }
    req = urllib.request.Request(
        L1000CDS2_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json",
                 "user-agent": "bryzant-lincs-matcher/1.0"},
        method="POST",
    )
    last_err: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_S * attempt)
            continue
    raise RuntimeError(f"L1000CDS^2 query failed after {MAX_RETRIES} attempts: {last_err}")


# -----------------------------------------------------------------------------#
# Cell-line filtering                                                           #
# -----------------------------------------------------------------------------#
def is_neuronal(cell_id: str) -> bool:
    if not cell_id:
        return False
    cid = cell_id.upper().replace("-", "")
    if cid in NEURONAL_CELL_IDS:
        return True
    for pfx in NEURONAL_PREFIX:
        if cid.startswith(pfx):
            return True
    if "NEURO" in cid or cid.startswith("GLI"):
        return True
    return False


# -----------------------------------------------------------------------------#
# Output                                                                        #
# -----------------------------------------------------------------------------#
OUTPUT_COLS = [
    "pert_id", "pert_iname", "cell_line", "dose", "dose_unit",
    "connectivity_score", "fdr", "n_genes_overlapped",
    "direction", "pubchem_id", "sig_id", "is_neuronal", "query_subset",
]


def hits_to_rows(hits: list[dict], direction: str,
                 input_up: int, input_down: int) -> list[dict]:
    """Normalize L1000CDS^2 hits into our output schema.

    Score is already Connectivity-Map-style (overlap-based, Kolmogorov-Smirnov
    enrichment per Lamb 2006 as extended by Duan 2016). We do NOT recompute it
    to avoid inventing a metric.

    FDR is NOT returned by L1000CDS^2 in the public API; we report NA and
    surface n_genes_overlapped so the user can apply a hypergeometric gate
    locally if needed.
    """
    rows = []
    for h in hits:
        ov = h.get("overlap", {}) or {}
        overlap_count = 0
        if isinstance(ov, dict):
            overlap_count = sum(len(v) for v in ov.values() if isinstance(v, list))
        cell = h.get("cell_id", "") or ""
        rows.append({
            "pert_id": h.get("pert_id", ""),
            "pert_iname": h.get("pert_desc", h.get("pert_iname", "")),
            "cell_line": cell,
            "dose": h.get("pert_dose", ""),
            "dose_unit": h.get("pert_dose_unit", ""),
            "connectivity_score": h.get("score", ""),
            "fdr": "NA",  # L1000CDS^2 REST does not return FDR
            "n_genes_overlapped": overlap_count,
            "direction": direction,   # 'reverse' or 'mimic'
            "pubchem_id": h.get("pubchem_id", ""),
            "sig_id": h.get("sig_id", ""),
            "is_neuronal": is_neuronal(cell),
        })
    return rows


def write_tsv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        fh.write("\t".join(OUTPUT_COLS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in OUTPUT_COLS) + "\n")


# -----------------------------------------------------------------------------#
# CLI                                                                           #
# -----------------------------------------------------------------------------#
def main() -> int:
    ap = argparse.ArgumentParser(description="LINCS L1000 connectivity matcher")
    ap.add_argument("--signature", required=True, type=Path,
                    help="TSV with gene + direction (UP/DOWN) or log2FC")
    ap.add_argument("--output", required=True, type=Path,
                    help="Output TSV path for hits")
    ap.add_argument("--top-n", type=int, default=30,
                    help="Top hits to keep after ranking (default: 30)")
    ap.add_argument("--cell-line-filter",
                    choices=["neuronal", "all"], default="all",
                    help="Restrict hits to neuronal-lineage cell lines (default: all, "
                         "report both but flag neuronal)")
    ap.add_argument("--direction", choices=["reverse", "mimic", "both"],
                    default="both",
                    help="Reversers = therapeutic candidates; mimics = disease-matching; "
                         "both = run two queries and concatenate (default: both)")
    ap.add_argument("--max-genes", type=int, default=150,
                    help="Cap input up/down lists (L1000CDS^2 recommends <=150 per side)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    log = (lambda *a, **k: None) if args.quiet else (lambda *a, **k: print(*a, **k, file=sys.stderr))

    # --- parse signature -----------------------------------------------------
    try:
        up, dn = parse_signature(args.signature, max_genes=args.max_genes)
    except Exception as e:
        print(f"ERROR parsing signature: {e}", file=sys.stderr)
        return 2
    log(f"[lincs] signature: {len(up)} UP, {len(dn)} DOWN (after cap={args.max_genes})")
    if not up and not dn:
        print("ERROR: signature has 0 up and 0 down genes.", file=sys.stderr)
        return 3
    log(f"[lincs] top UP:   {up[:10]}")
    log(f"[lincs] top DOWN: {dn[:10]}")

    # --- run queries ---------------------------------------------------------
    # L1000CDS^2 caps response at 50 hits per query. To increase neuronal-
    # cell-line recall we run TWO queries per direction:
    #   (a) the full signature (broad coverage)
    #   (b) the high-confidence panel subset (first ~25 genes per side)
    # and union the results (dedup by sig_id).
    all_rows: list[dict] = []
    modes = []
    if args.direction in ("reverse", "both"):
        modes.append(("reverse", False))
    if args.direction in ("mimic", "both"):
        modes.append(("mimic", True))

    panel_up = up[: min(25, len(up))]
    panel_dn = dn[: min(25, len(dn))]
    # L1000CDS^2 ranks by raw overlap count; with tiny signatures the cell
    # lines with sparser platforms (NPC, NEU, SHSY5Y) have a fair shot at the
    # top-50 because overlap is bounded by signature size. So we run a
    # deliberately small high-confidence anchor query to surface neuronal hits.
    anchor_up = up[: min(8, len(up))]
    anchor_dn = dn[: min(10, len(dn))]

    seen: set[tuple[str, str]] = set()
    for label, aggravate in modes:
        for sub, sub_up, sub_dn in [
            ("full", up, dn),
            ("panel25", panel_up, panel_dn),
            ("anchors", anchor_up, anchor_dn),
        ]:
            log(f"[lincs] querying L1000CDS^2 aggravate={aggravate} "
                f"({label}/{sub} up={len(sub_up)} dn={len(sub_dn)})...")
            t0 = time.time()
            try:
                resp = query_l1000cds2(sub_up, sub_dn, aggravate=aggravate)
            except Exception as e:
                print(f"ERROR L1000CDS^2 query ({label}/{sub}): {e}", file=sys.stderr)
                return 4
            dt = time.time() - t0
            hits = resp.get("topMeta", []) or []
            log(f"[lincs]   -> {len(hits)} hits in {dt:.1f}s "
                f"(shareId={resp.get('shareId','?')})")
            new_rows = hits_to_rows(hits, label, len(sub_up), len(sub_dn))
            for r in new_rows:
                key = (r["sig_id"] or f"{r['pert_id']}_{r['cell_line']}", label)
                if key in seen:
                    continue
                seen.add(key)
                r["query_subset"] = sub
                all_rows.append(r)

    if not all_rows:
        print("WARN: no hits returned from L1000CDS^2.", file=sys.stderr)
        write_tsv([], args.output)
        return 0

    # --- cell-line filter ----------------------------------------------------
    if args.cell_line_filter == "neuronal":
        neuronal = [r for r in all_rows if r["is_neuronal"]]
        if not neuronal:
            log("[lincs] WARN: neuronal filter matched 0 hits; falling back to all cell lines")
        else:
            all_rows = neuronal
            log(f"[lincs] neuronal filter: {len(all_rows)} hits")

    # --- rank + trim to top-N ------------------------------------------------
    # L1000CDS^2 score: higher = better match (for both reverse and mimic runs).
    def _score(r):
        try:
            return float(r["connectivity_score"])
        except Exception:
            return -1.0
    # Sort: neuronal first (if filter=all, still surface them), then by score desc.
    all_rows.sort(key=lambda r: (not r["is_neuronal"], -_score(r)))

    # Per-direction cap: top-N reversers + top-N mimics (if both)
    out_rows: list[dict] = []
    for label, _ in modes:
        kept = [r for r in all_rows if r["direction"] == label][: args.top_n]
        out_rows.extend(kept)

    write_tsv(out_rows, args.output)
    log(f"[lincs] wrote {len(out_rows)} rows to {args.output}")

    # --- stdout one-liner summary (machine-parseable) ------------------------
    n_reverse = sum(1 for r in out_rows if r["direction"] == "reverse")
    n_mimic = sum(1 for r in out_rows if r["direction"] == "mimic")
    n_neu = sum(1 for r in out_rows if r["is_neuronal"])
    print(f"signature_up={len(up)} signature_down={len(dn)} "
          f"reverse_hits={n_reverse} mimic_hits={n_mimic} "
          f"neuronal_hits={n_neu} output={args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
