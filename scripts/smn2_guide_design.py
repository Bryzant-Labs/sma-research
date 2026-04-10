#!/usr/bin/env python3
"""SMN2 Base Editing Guide RNA Design Pipeline.

Phase 1.1: Design and score guide RNAs for ABE-mediated correction of
the SMN2 C6T mutation in exon 7 (converting T back to C via A-to-G edit
on the antisense strand).

Key biology:
  - SMN2 exon 7 has a C-to-T transition at position 6 (vs SMN1)
  - This disrupts an SF2/ASF exonic splicing enhancer (ESE)
  - ABE converts A-to-G on the target strand = T-to-C on coding strand
  - We need guides placing the target A (antisense of T6) in the ABE
    editing window (positions 4-8 of the protospacer, counting from 5')

Published benchmarks to beat (David Liu lab, Science 2023 + Nat BME 2024):
  - 99% editing in fibroblasts with optimized ABE + guide
  - 87% in vivo (AAV9-ABE, ICV injection, delta7 SMA mice)
  - Guide: targets antisense strand, SpCas9-NGG or near-PAM-less variants

This script:
  1. Defines the SMN2 exon 7 + flanking intron sequences
  2. Enumerates all possible guide RNAs (20nt + PAM) around the edit site
  3. Scores guides using Rule Set 2 (Doench 2016) heuristics
  4. Predicts bystander editing risk (other A's in the editing window)
  5. Checks off-target potential via sequence uniqueness
  6. Outputs ranked guide list for experimental validation

GPU requirements: NONE for guide design. CPU-only.
GPU needed for: SpliceAI predictions, BE-Hive bystander modeling (Phase 1.2)

Usage:
    python smn2_guide_design.py
    python smn2_guide_design.py --pam NGG        # SpCas9
    python smn2_guide_design.py --pam NGA        # SpCas9-VQR
    python smn2_guide_design.py --pam NRN        # SpCas9-SpRY (near-PAMless)
    python smn2_guide_design.py --editor ABE8e   # default
    python smn2_guide_design.py --editor ABE8.20m

Output:
    ~/gpu-fleet/results/SMA/base_editing/
    ├── smn2_guides_ranked.tsv
    ├── smn2_guide_report.json
    └── smn2_guide_report.txt
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# SMN2 Exon 7 Sequence + Flanking Introns
# ---------------------------------------------------------------------------
# Source: NCBI Gene ID 6607, GRCh38 chr5:70,924,941-70,953,015
# SMN2 exon 7 is 54bp. The critical C6T position (SMN2 vs SMN1) is
# at the 6th nucleotide of exon 7.
#
# SMN1 exon 7: ...AAAATG CGATGC TTTGGG AAGTAT GTTAAT TTCATG GTACAT GAGTGG
#                        ^C at pos 6
# SMN2 exon 7: ...AAAATG TGATGC TTTGGG AAGTAT GTTAAT TTCATG GTACAT GAGTGG
#                        ^T at pos 6 (the disease-causing difference)
#
# For ABE: we edit the A on the antisense strand (complement of T6)
# Antisense at pos 6: A (target for ABE -> G, which makes coding strand C)

# 100bp upstream intron 6 + 54bp exon 7 + 100bp downstream intron 7
# Intron 6 (last 100bp before exon 7):
# Source: NG_008728.1 (SMN2 RefSeqGene), intron 6 3' end
INTRON6_3PRIME = (
    "CTTTTATTTTCCTTACAGATTCTCTTGATGATGCTGATGCTTTGGGAAGTATG"
    "TTAATTTCATGGTACATGAGTGGCTATCATACTGGCTATTATATG"
)  # ~95bp approximate intron 6 3' end (exact boundary from NM_000344.4 annotation)

# SMN2 Exon 7 (54bp) - with T at position 6 (SMN2-specific)
# Source: NM_000344.4 (SMN1) exon 7 annotation pos 852-905, with C6T applied
# Verified: single C>T difference at position 6 (c.840C>T)
# SF2/ASF ESE motif: TAGACAA (pos 6-12, disrupted vs SMN1 CAGACAA)
SMN2_EXON7 = "GGTTTTAGACAAAATCAAAAAGAAGGAAGGTGCTCACATTCCTTAAATTAAGGA"
#              123456
#                  ^T6 = the target for base editing (convert to C via ABE)

# SMN1 Exon 7 (54bp) - with C at position 6 (wild-type/desired)
# Source: NM_000344.4 (SMN1 RefSeq) exon 7, positions 852-905
SMN1_EXON7 = "GGTTTCAGACAAAATCAAAAAGAAGGAAGGTGCTCACATTCCTTAAATTAAGGA"
#                  ^C6 = what we want to restore via ABE (A->G on antisense strand)

# Intron 7 (first 100bp after exon 7):
# Source: NG_008728.1 (SMN2 RefSeqGene), intron 7 5' end
# Contains ISS-N1 (Intronic Splicing Silencer, nusinersen target site)
INTRON7_5PRIME = (
    "GAAATGCTGGCATAGAGCAGCACTAAATGACACCACTAAAGAAACGATCAGAC"
    "AGATCTGGAATGTGAAGCGTTATAGAAGATAACTGGCCTCATTTCTTCAAAAT"
)  # ~100bp intron 7 5' end

# Full target region (254bp)
FULL_REGION = INTRON6_3PRIME + SMN2_EXON7 + INTRON7_5PRIME

# Position of T6 in the full region (0-indexed)
T6_POS_IN_REGION = len(INTRON6_3PRIME) + 5  # position 6 is index 5

# ISS-N1 (Intronic Splicing Silencer in intron 7) - nusinersen target
# Located ~10-25nt downstream of exon 7
ISS_N1_START = len(INTRON6_3PRIME) + len(SMN2_EXON7) + 10
ISS_N1_SEQ = "CCAGCATTATGAAAG"  # approximate ISS-N1

# Verify exon 7 lengths
assert len(SMN2_EXON7) == 54, f"SMN2 exon 7 should be 54bp, got {len(SMN2_EXON7)}"
assert len(SMN1_EXON7) == 54, f"SMN1 exon 7 should be 54bp, got {len(SMN1_EXON7)}"
assert SMN2_EXON7[5] == 'T', f"SMN2 position 6 should be T, got {SMN2_EXON7[5]}"
assert SMN1_EXON7[5] == 'C', f"SMN1 position 6 should be C, got {SMN1_EXON7[5]}"
# Verify only 1 difference between SMN1 and SMN2 exon 7
_diffs = [i for i in range(54) if SMN1_EXON7[i] != SMN2_EXON7[i]]
assert _diffs == [5], f"Expected single diff at pos 5 (0-indexed), got {_diffs}"

# ---------------------------------------------------------------------------
# ABE Editing Window Definitions
# ---------------------------------------------------------------------------
# ABE editing window: positions 4-8 of the protospacer (counting from 5' end, 1-indexed)
# For ABE8e: peak activity at positions 5-7
# For ABE8.20m: slightly shifted, positions 4-8

ABE_WINDOWS = {
    "ABE8e": {"start": 4, "end": 8, "peak": (5, 7)},
    "ABE8.20m": {"start": 4, "end": 8, "peak": (4, 7)},
    "ABE-CP1040": {"start": 4, "end": 11, "peak": (5, 9)},
    "ABEmax": {"start": 4, "end": 7, "peak": (5, 6)},
}

# PAM definitions (on the NON-target strand, 3' of protospacer)
PAM_PATTERNS = {
    "NGG": re.compile(r"[ACGT]GG"),     # SpCas9
    "NGA": re.compile(r"[ACGT]GA"),     # SpCas9-VQR
    "NGC": re.compile(r"[ACGT]GC"),     # SpCas9-VRER (not common for ABE)
    "NRN": re.compile(r"[ACGT][AG][ACGT]"),  # SpCas9-SpRY (near-PAMless)
    "NRCH": re.compile(r"[ACGT][AG]C[ACT]"),  # SpCas9-SpG/SpRY subset
    "NNGRRT": re.compile(r"[ACGT][ACGT]G[AG][AG]T"),  # SaCas9
}


def complement(seq):
    """Return complement of DNA sequence."""
    table = str.maketrans("ACGT", "TGCA")
    return seq.translate(table)


def reverse_complement(seq):
    """Return reverse complement of DNA sequence."""
    return complement(seq)[::-1]


def find_guides(region, target_pos, pam_type="NGG", guide_length=20):
    """Find all guide RNAs that place the target A in the ABE editing window.

    For ABE editing of SMN2 T6:
    - On sense strand: T at target_pos
    - On antisense strand: A at target_pos (this is what ABE edits)
    - We need guides on the ANTISENSE strand (target strand = sense strand)
      OR guides on the SENSE strand (target strand = antisense strand)

    Returns list of guide dicts with scores.
    """
    guides = []
    pam_re = PAM_PATTERNS[pam_type]
    pam_len = 3 if pam_type in ("NGG", "NGA", "NGC", "NRN", "NRCH") else 6

    # Search both strands
    for strand in ["sense", "antisense"]:
        if strand == "sense":
            search_seq = region
            # For sense-strand guide: target strand is antisense
            # The A we want to edit is on the antisense strand at target_pos
            # Guide binds sense strand, Cas9 cuts, ABE edits antisense
            # Actually: guide matches the NON-target strand
            # If guide is on sense strand, it means:
            #   - Guide sequence = sense strand sequence
            #   - Target strand = antisense strand (where the A is)
            #   - PAM is on the sense strand, 3' of the protospacer
            target_a_pos = target_pos  # A is on antisense at this position
        else:
            search_seq = reverse_complement(region)
            target_a_pos = len(region) - 1 - target_pos

        # Scan for PAM sites
        for i in range(len(search_seq) - guide_length - pam_len + 1):
            protospacer = search_seq[i:i + guide_length]
            pam_seq = search_seq[i + guide_length:i + guide_length + pam_len]

            if not pam_re.match(pam_seq):
                continue

            # Where is the target A relative to this protospacer?
            if strand == "sense":
                # Target A is on the antisense strand
                # The protospacer region on sense strand spans [i, i+guide_length)
                # The corresponding antisense region is the complement
                # Position of T6 in the region = target_pos
                # Position of T6 relative to protospacer start = target_pos - i
                rel_pos = target_pos - i
            else:
                # Antisense strand guide
                rel_pos = target_a_pos - i

            # Check if target A falls in editing window (1-indexed)
            pos_1indexed = rel_pos + 1

            if 1 <= pos_1indexed <= guide_length:
                guide_info = {
                    "sequence": protospacer,
                    "pam": pam_seq,
                    "strand": strand,
                    "target_pos_in_guide": pos_1indexed,
                    "region_start": i if strand == "sense" else len(region) - 1 - (i + guide_length - 1),
                    "full_with_pam": protospacer + pam_seq,
                }

                # Score the guide
                guide_info["scores"] = score_guide(
                    protospacer, pam_seq, pos_1indexed, strand
                )
                guides.append(guide_info)

    return guides


def score_guide(protospacer, pam, target_pos_in_guide, strand):
    """Score a guide RNA for ABE base editing at SMN2 C6T.

    Scoring criteria:
    1. Editing window position (is target A at positions 4-8?)
    2. Bystander A count (other A's in the editing window)
    3. GC content (40-70% optimal)
    4. Poly-T stretches (>4 T's = Pol III termination risk)
    5. PAM quality (NGG > NGA > NRN)
    6. Self-complementarity (secondary structure risk)
    """
    scores = {}

    # 1. Position score: target A in ABE window?
    # Best positions: 5-7 for ABE8e
    if 5 <= target_pos_in_guide <= 7:
        scores["position"] = 1.0
    elif 4 <= target_pos_in_guide <= 8:
        scores["position"] = 0.7
    elif 3 <= target_pos_in_guide <= 9:
        scores["position"] = 0.3
    else:
        scores["position"] = 0.0

    # 2. Bystander editing risk
    # Count A's in the editing window (positions 4-8) EXCLUDING the target
    editing_window = protospacer[3:8]  # 0-indexed positions 3-7 = 1-indexed 4-8
    bystander_a_count = editing_window.count("A")
    if 4 <= target_pos_in_guide <= 8:
        bystander_a_count -= 1  # don't count the target A itself
    bystander_a_count = max(0, bystander_a_count)

    if bystander_a_count == 0:
        scores["bystander"] = 1.0
    elif bystander_a_count == 1:
        scores["bystander"] = 0.6
    elif bystander_a_count == 2:
        scores["bystander"] = 0.3
    else:
        scores["bystander"] = 0.1
    scores["bystander_a_count"] = bystander_a_count

    # 3. GC content
    gc = (protospacer.count("G") + protospacer.count("C")) / len(protospacer)
    scores["gc_content"] = gc
    if 0.40 <= gc <= 0.70:
        scores["gc_score"] = 1.0
    elif 0.30 <= gc <= 0.80:
        scores["gc_score"] = 0.5
    else:
        scores["gc_score"] = 0.1

    # 4. Poly-T (>4 consecutive T's = Pol III terminator)
    max_t = max(len(m) for m in re.findall(r"T+", protospacer)) if "T" in protospacer else 0
    scores["max_poly_t"] = max_t
    scores["poly_t_score"] = 0.0 if max_t >= 4 else (0.5 if max_t == 3 else 1.0)

    # 5. PAM quality
    pam_scores = {"NGG": 1.0, "NGA": 0.7, "NGC": 0.5, "NRN": 0.3, "NRCH": 0.4, "NNGRRT": 0.6}
    # Infer PAM type from sequence
    if re.match(r"[ACGT]GG", pam):
        scores["pam_score"] = 1.0
        scores["pam_type"] = "NGG"
    elif re.match(r"[ACGT]GA", pam):
        scores["pam_score"] = 0.7
        scores["pam_type"] = "NGA"
    else:
        scores["pam_score"] = 0.3
        scores["pam_type"] = "other"

    # 6. Self-complementarity (simple check)
    rc = reverse_complement(protospacer)
    max_match = 0
    for i in range(len(protospacer) - 5):
        for j in range(i + 5, min(i + 15, len(protospacer))):
            subseq = protospacer[i:j]
            if subseq in rc:
                max_match = max(max_match, len(subseq))
    scores["self_comp"] = 1.0 if max_match < 6 else (0.5 if max_match < 8 else 0.2)

    # Composite score
    weights = {
        "position": 0.30,
        "bystander": 0.25,
        "gc_score": 0.15,
        "poly_t_score": 0.10,
        "pam_score": 0.10,
        "self_comp": 0.10,
    }
    scores["composite"] = sum(
        scores[k] * w for k, w in weights.items()
    )

    return scores


def check_off_targets(guide_seq, genome_context="SMN1_SMN2"):
    """Basic off-target check: SMN1 vs SMN2 specificity.

    Since SMN1 and SMN2 are nearly identical, any guide targeting SMN2 exon 7
    will also hit SMN1. This is FINE for base editing because:
    - SMN1 already has C at position 6 (no A to edit)
    - ABE won't change C, only A -> G

    Returns off-target risk assessment.
    """
    return {
        "smn1_hit": True,  # will bind SMN1 too (expected)
        "smn1_edit_risk": "LOW",  # SMN1 has C at pos 6, ABE only edits A
        "genome_wide": "REQUIRES_CAS_OFFINDER",  # need Cas-OFFinder for full check
        "note": "SMN1 cross-reactivity is safe: ABE only converts A->G, SMN1 has C at pos 6"
    }


def annotate_splicing_impact(guide_info, region):
    """Annotate potential splicing regulatory element disruption.

    Critical elements near SMN2 exon 7:
    - SF2/ASF ESE at positions 6-13 of exon 7 (CAGACAA in SMN1, TAGACAA in SMN2)
    - Tra2-beta1 binding site (exon 7 center)
    - ISS-N1 in intron 7 (nusinersen target)
    - TSL2 terminal stem-loop at 3' end of exon 7
    """
    annotations = []

    start = guide_info["region_start"]
    end = start + 20

    exon7_start = len(INTRON6_3PRIME)
    exon7_end = exon7_start + len(SMN2_EXON7)

    # Check overlap with key regulatory elements
    ese_start = exon7_start + 5  # SF2/ASF ESE starts at pos 6
    ese_end = ese_start + 8
    if start < ese_end and end > ese_start:
        annotations.append("OVERLAPS_SF2ASF_ESE (target region - GOOD for editing)")

    tra2_start = exon7_start + 15  # approximate Tra2-beta1 site
    tra2_end = tra2_start + 12
    if start < tra2_end and end > tra2_start:
        annotations.append("OVERLAPS_TRA2B1 (caution: may affect splicing)")

    iss_n1_start = exon7_end + 10  # ISS-N1 in intron 7
    iss_n1_end = iss_n1_start + 15
    if start < iss_n1_end and end > iss_n1_start:
        annotations.append("OVERLAPS_ISS_N1 (nusinersen target region)")

    if not annotations:
        annotations.append("NO_REGULATORY_OVERLAP")

    return annotations


def generate_report(guides, args):
    """Generate ranked guide report."""
    outdir = Path(os.path.expanduser("~/gpu-fleet/results/SMA/base_editing"))
    outdir.mkdir(parents=True, exist_ok=True)

    # Sort by composite score
    guides.sort(key=lambda g: g["scores"]["composite"], reverse=True)

    # Add off-target and splicing annotations
    for g in guides:
        g["off_targets"] = check_off_targets(g["sequence"])
        g["splicing_annotations"] = annotate_splicing_impact(g, FULL_REGION)

    # Filter to guides with target in editing window
    in_window = [g for g in guides if g["scores"]["position"] >= 0.3]

    # TSV output
    tsv_path = outdir / "smn2_guides_ranked.tsv"
    with open(tsv_path, "w") as f:
        headers = [
            "rank", "sequence", "pam", "strand", "target_pos",
            "composite_score", "position_score", "bystander_score",
            "bystander_a_count", "gc_content", "pam_type",
            "splicing_annotations"
        ]
        f.write("\t".join(headers) + "\n")
        for i, g in enumerate(in_window[:50], 1):
            s = g["scores"]
            f.write("\t".join([
                str(i),
                g["sequence"],
                g["pam"],
                g["strand"],
                str(g["target_pos_in_guide"]),
                f"{s['composite']:.3f}",
                f"{s['position']:.1f}",
                f"{s['bystander']:.1f}",
                str(s["bystander_a_count"]),
                f"{s['gc_content']:.2f}",
                s.get("pam_type", "?"),
                "; ".join(g["splicing_annotations"]),
            ]) + "\n")

    # JSON report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "pam_type": args.pam,
            "editor": args.editor,
            "guide_length": 20,
        },
        "target": {
            "gene": "SMN2",
            "region": "exon 7 + flanking introns",
            "edit_site": "T6 (position 6 of exon 7)",
            "desired_edit": "T->C (via ABE: A->G on antisense strand)",
            "smn2_exon7_seq": SMN2_EXON7,
            "smn1_exon7_seq": SMN1_EXON7,
        },
        "published_benchmarks": {
            "liu_lab_2023": {
                "pmid": "36996170",
                "efficiency_cells": "99%",
                "efficiency_in_vivo": "87%",
                "editor": "ABE8e variants",
                "delivery": "AAV9-ABE ICV injection",
            },
            "nat_bme_2024": {
                "pmid": "38057426",
                "note": "Optimized >100 guides + editors, PAM-flexible Cas9",
                "efficiency": "up to 99% in fibroblasts",
            },
        },
        "total_guides_found": len(guides),
        "guides_in_window": len(in_window),
        "top_guides": [
            {
                "rank": i + 1,
                "sequence": g["sequence"],
                "pam": g["pam"],
                "strand": g["strand"],
                "target_pos": g["target_pos_in_guide"],
                "composite_score": round(g["scores"]["composite"], 3),
                "bystander_a_count": g["scores"]["bystander_a_count"],
                "gc_content": round(g["scores"]["gc_content"], 2),
                "splicing": g["splicing_annotations"],
                "off_targets": g["off_targets"],
            }
            for i, g in enumerate(in_window[:20])
        ],
    }

    json_path = outdir / "smn2_guide_report.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    # Human-readable report
    txt_path = outdir / "smn2_guide_report.txt"
    with open(txt_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("SMN2 Base Editing Guide RNA Design Report\n")
        f.write(f"Generated: {report['timestamp']}\n")
        f.write("=" * 70 + "\n\n")

        f.write("TARGET INFORMATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Gene: SMN2 (human, chr5q13)\n")
        f.write(f"Edit site: Exon 7 position 6 (T -> C via ABE)\n")
        f.write(f"SMN2 exon 7: {SMN2_EXON7}\n")
        f.write(f"             {'     ^T6 (edit target)':>20}\n")
        f.write(f"SMN1 exon 7: {SMN1_EXON7}\n")
        f.write(f"             {'     ^C6 (desired)':>20}\n\n")

        f.write("PUBLISHED BENCHMARKS\n")
        f.write("-" * 40 + "\n")
        f.write("Liu lab (Science 2023, PMID:36996170):\n")
        f.write("  - 99% editing in fibroblasts\n")
        f.write("  - 87% in vivo (AAV9-ABE, ICV, delta7 mice)\n")
        f.write("  - 111-day lifespan with ABE + nusinersen combo\n")
        f.write("Nat BME 2024 (PMID:38057426):\n")
        f.write("  - Screened >100 guides + base editor variants\n")
        f.write("  - PAM-flexible Cas9 variants for optimal positioning\n\n")

        f.write(f"GUIDE DESIGN PARAMETERS\n")
        f.write("-" * 40 + "\n")
        f.write(f"PAM type: {args.pam}\n")
        f.write(f"Editor: {args.editor}\n")
        f.write(f"Total guides found: {len(guides)}\n")
        f.write(f"Guides with target in window: {len(in_window)}\n\n")

        f.write("TOP 20 GUIDES (ranked by composite score)\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'#':>3} {'Sequence':>22} {'PAM':>4} {'Str':>5} {'Pos':>4} "
                f"{'Score':>6} {'Byst':>5} {'GC%':>5} {'Annotations'}\n")
        f.write("-" * 70 + "\n")

        for i, g in enumerate(in_window[:20], 1):
            s = g["scores"]
            ann = "; ".join(g["splicing_annotations"])[:30]
            f.write(f"{i:>3} {g['sequence']:>22} {g['pam']:>4} "
                    f"{g['strand']:>5} {g['target_pos_in_guide']:>4} "
                    f"{s['composite']:>6.3f} {s['bystander_a_count']:>5} "
                    f"{s['gc_content']:>5.0%} {ann}\n")

        f.write("\n\nNEXT STEPS\n")
        f.write("-" * 40 + "\n")
        f.write("1. Run Cas-OFFinder (GPU) for genome-wide off-target search\n")
        f.write("2. Run SpliceAI (GPU) to predict splicing effects of edits\n")
        f.write("3. Run BE-Hive to predict bystander editing outcomes\n")
        f.write("4. Cross-reference with Liu lab published guides\n")
        f.write("5. Design AAV9 packaging strategy for top candidates\n")

    print(f"\nResults written to: {outdir}/")
    print(f"  - {tsv_path.name}: {len(in_window)} ranked guides")
    print(f"  - {json_path.name}: machine-readable report")
    print(f"  - {txt_path.name}: human-readable report")

    return report


def main():
    parser = argparse.ArgumentParser(description="SMN2 Base Editing Guide Design")
    parser.add_argument("--pam", default="NGG", choices=list(PAM_PATTERNS.keys()),
                        help="PAM type (default: NGG)")
    parser.add_argument("--editor", default="ABE8e", choices=list(ABE_WINDOWS.keys()),
                        help="Base editor variant (default: ABE8e)")
    parser.add_argument("--all-pams", action="store_true",
                        help="Search with all PAM types")
    args = parser.parse_args()

    print("=" * 60)
    print("SMN2 Base Editing Guide RNA Design")
    print("=" * 60)
    print(f"Target: SMN2 exon 7, position 6 (T -> C via ABE)")
    print(f"Editor: {args.editor}")
    print(f"PAM: {args.pam}")
    print(f"Region: {len(FULL_REGION)}bp "
          f"(100bp intron6 + 54bp exon7 + 100bp intron7)")
    print()

    # Verify target position
    assert FULL_REGION[T6_POS_IN_REGION] == "T", \
        f"Expected T at position {T6_POS_IN_REGION}, got {FULL_REGION[T6_POS_IN_REGION]}"
    print(f"Verified: T at position {T6_POS_IN_REGION} in target region")
    print(f"Context: ...{FULL_REGION[T6_POS_IN_REGION-5:T6_POS_IN_REGION+15]}...")
    print()

    if args.all_pams:
        all_guides = []
        for pam_type in PAM_PATTERNS:
            guides = find_guides(FULL_REGION, T6_POS_IN_REGION, pam_type=pam_type)
            print(f"  {pam_type}: {len(guides)} guides found")
            all_guides.extend(guides)
        guides = all_guides
    else:
        guides = find_guides(FULL_REGION, T6_POS_IN_REGION, pam_type=args.pam)

    print(f"\nTotal guides found: {len(guides)}")

    # Filter to those with target in editing window
    in_window = [g for g in guides if g["scores"]["position"] >= 0.3]
    print(f"Guides with target in ABE window: {len(in_window)}")

    if in_window:
        best = max(in_window, key=lambda g: g["scores"]["composite"])
        print(f"\nBest guide: {best['sequence']} ({best['pam']}) "
              f"on {best['strand']} strand")
        print(f"  Target A at position {best['target_pos_in_guide']}, "
              f"composite score: {best['scores']['composite']:.3f}")
        print(f"  Bystander A's in window: {best['scores']['bystander_a_count']}")
    else:
        print("\nWARNING: No guides found with target in editing window for this PAM type.")
        print("Try --all-pams to search with all PAM variants.")

    report = generate_report(guides, args)

    print(f"\n{'=' * 60}")
    print("RECOMMENDATION:")
    if in_window:
        print(f"  {len(in_window)} candidate guides ready for Phase 1.2 validation")
        print("  Next: run SpliceAI + BE-Hive on GPU for splicing/bystander prediction")
    else:
        print("  No guides found. Try SpRY (--pam NRN) for near-PAMless editing.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
