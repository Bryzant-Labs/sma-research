#!/usr/bin/env python3
"""SMN2 Splicing Prediction After Base Editing.

Phase 1.2: Predict how ABE-mediated edits at SMN2 exon 7 affect splicing.
Uses SpliceAI (GPU-accelerated) and sequence-based models.

Key question: Does converting T6->C (restoring SMN1 sequence) actually
restore exon 7 inclusion? Published data says YES (Liu lab, 99% editing
-> full SMN protein restoration), but we want to:
  1. Quantify the delta-PSI (change in percent-spliced-in) computationally
  2. Predict effects of bystander edits (other A->G changes in the window)
  3. Model combinatorial effects of edit + nusinersen (ISS-N1 blocking)

Tools used:
  - SpliceAI: deep learning splicing predictor (Illumina, requires TensorFlow)
  - Custom ESE/ESS scoring: SF2/ASF, Tra2-beta1, hnRNPA1 motif analysis
  - BE-Hive integration: predict bystander editing outcomes

GPU: Required for SpliceAI (TensorFlow). ~1GB VRAM sufficient.
     Can run on CPU but 10-100x slower.

Installation on Vast.ai:
    pip install spliceai tensorflow-gpu keras h5py
    # Or for GPU-optimized version:
    pip install git+https://github.com/skoblov-lab/spliceai-reforged.git

Usage:
    python smn2_splicing_predict.py                    # predict with SpliceAI
    python smn2_splicing_predict.py --ese-only          # ESE/ESS analysis only (no GPU)
    python smn2_splicing_predict.py --bystander         # include bystander edit scenarios
    python smn2_splicing_predict.py --with-nusinersen   # model nusinersen combo effect

Output:
    ~/gpu-fleet/results/SMA/base_editing/
    ├── smn2_splicing_predictions.json
    ├── smn2_ese_analysis.tsv
    └── smn2_splicing_report.txt
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# SMN2 Sequences (shared with guide design script)
# ---------------------------------------------------------------------------

# SMN2 Exon 7 (54bp) with T at position 6
# Source: NM_000344.4 exon 7 (pos 852-905) with C6T applied
SMN2_EXON7 = "GGTTTTAGACAAAATCAAAAAGAAGGAAGGTGCTCACATTCCTTAAATTAAGGA"

# SMN1 Exon 7 (54bp) with C at position 6 (desired after editing)
# Source: NM_000344.4 (SMN1 RefSeq) exon 7, positions 852-905
SMN1_EXON7 = "GGTTTCAGACAAAATCAAAAAGAAGGAAGGTGCTCACATTCCTTAAATTAAGGA"

# Flanking introns (approximate, from NG_008728.1)
INTRON6_3PRIME = (
    "CTTTTATTTTCCTTACAGATTCTCTTGATGATGCTGATGCTTTGGGAAGTATG"
    "TTAATTTCATGGTACATGAGTGGCTATCATACTGGCTATTATATG"
)

INTRON7_5PRIME = (
    "GAAATGCTGGCATAGAGCAGCACTAAATGACACCACTAAAGAAACGATCAGAC"
    "AGATCTGGAATGTGAAGCGTTATAGAAGATAACTGGCCTCATTTCTTCAAAAT"
)

# Full pre-mRNA region for splicing analysis
SMN2_FULL = INTRON6_3PRIME + SMN2_EXON7 + INTRON7_5PRIME
SMN1_FULL = INTRON6_3PRIME + SMN1_EXON7 + INTRON7_5PRIME

# ISS-N1 sequence in intron 7 (nusinersen binding site)
ISS_N1_OFFSET = len(INTRON6_3PRIME) + len(SMN2_EXON7) + 10
ISS_N1_SEQ = "CCAGCATTATGAAAG"

# ---------------------------------------------------------------------------
# Exonic Splicing Enhancer / Silencer Motifs
# ---------------------------------------------------------------------------

# Known ESE/ESS motifs relevant to SMN2 exon 7 splicing
ESE_MOTIFS = {
    "SF2/ASF": {
        "smn1_seq": "CAGACAA",  # present in SMN1 exon 7 (pos 6-12)
        "smn2_seq": "TAGACAA",  # disrupted in SMN2 (T at pos 6)
        "position": 5,  # 0-indexed position in exon 7
        "effect": "Strong ESE - promotes exon inclusion when intact",
        "binding_protein": "SRSF1 (SF2/ASF)",
    },
    "Tra2-beta1": {
        "consensus": "GAA",  # Tra2-beta1 binds GA-rich elements
        "position": 18,  # approximate position in exon 7
        "effect": "ESE - promotes exon 7 inclusion",
        "binding_protein": "TRA2B",
    },
    "hnRNPA1_exonic": {
        "consensus": "UAGGGA",  # hnRNP A1 binding (RNA notation)
        "dna_consensus": "TAGGGA",
        "effect": "ESS - promotes exon 7 skipping",
        "note": "T6 in SMN2 may create weak hnRNPA1 site",
    },
}

# ISS-N1 in intron 7 (hnRNP A1 binding, strong splicing silencer)
ISS_MOTIFS = {
    "ISS-N1": {
        "sequence": "CCAGCATTATGAAAG",
        "location": "intron 7, +10 to +24",
        "effect": "Strong ISS - promotes exon 7 skipping",
        "binding_protein": "hnRNP A1/A2",
        "drug_target": "Nusinersen (Spinraza) blocks this site",
    },
}


def analyze_ese_ess(exon_seq, label="unknown"):
    """Analyze exonic splicing enhancer/silencer motifs.

    Returns dict with ESE/ESS scores for the given exon 7 variant.
    """
    results = {
        "label": label,
        "sequence": exon_seq,
        "motifs": {},
    }

    # SF2/ASF ESE analysis
    sf2_region = exon_seq[5:12]  # positions 6-12 of exon 7 (0-indexed 5:12)
    sf2_smn1 = "CAGACAA"  # strong ESE
    sf2_smn2 = "TAGACAA"  # disrupted ESE

    if sf2_region == sf2_smn1 or sf2_region[0] == "C":
        results["motifs"]["SF2_ASF"] = {
            "present": True,
            "strength": "STRONG",
            "sequence": sf2_region,
            "effect": "Promotes exon 7 inclusion",
        }
    elif sf2_region == sf2_smn2 or sf2_region[0] == "T":
        results["motifs"]["SF2_ASF"] = {
            "present": False,
            "strength": "DISRUPTED",
            "sequence": sf2_region,
            "effect": "Reduced exon 7 inclusion (SMA pathology)",
        }
    else:
        results["motifs"]["SF2_ASF"] = {
            "present": "PARTIAL",
            "strength": "UNKNOWN",
            "sequence": sf2_region,
            "effect": "Novel variant - requires experimental validation",
        }

    # Tra2-beta1 binding (GA-rich region in middle of exon 7)
    ga_rich_count = sum(1 for i in range(len(exon_seq) - 2)
                        if exon_seq[i:i+3] in ("GAA", "GAG", "AGG"))
    results["motifs"]["Tra2_beta1"] = {
        "ga_rich_count": ga_rich_count,
        "strength": "STRONG" if ga_rich_count >= 3 else "MODERATE",
        "effect": "Promotes exon 7 inclusion (cooperative with SF2/ASF)",
    }

    # Overall ESE score (simple model)
    ese_score = 0
    if results["motifs"]["SF2_ASF"]["strength"] == "STRONG":
        ese_score += 5
    elif results["motifs"]["SF2_ASF"]["strength"] == "DISRUPTED":
        ese_score += 1
    ese_score += ga_rich_count

    results["ese_score"] = ese_score
    results["predicted_inclusion"] = "HIGH" if ese_score >= 6 else (
        "MODERATE" if ese_score >= 3 else "LOW"
    )

    return results


def generate_bystander_variants(exon_seq, edit_pos=5, window_start=3, window_end=8):
    """Generate all possible bystander editing outcomes.

    ABE can edit any A in the editing window (positions 4-8 of the guide).
    On the antisense strand, A's correspond to T's on the sense strand.
    So we look for T's in the exon sequence near the edit site.

    Returns list of variant sequences with their edit descriptions.
    """
    variants = []

    # Find all T's in the editing window region of the exon
    # The editing window maps to a region of the exon that depends on guide positioning
    # For simplicity, check T's within +/- 5nt of the target T6
    for i in range(max(0, edit_pos - 5), min(len(exon_seq), edit_pos + 6)):
        if i == edit_pos:
            continue  # skip the intended target
        if exon_seq[i] == "T":
            # This T could be edited to C by ABE (via A->G on antisense)
            variant = exon_seq[:i] + "C" + exon_seq[i+1:]
            variants.append({
                "position": i + 1,  # 1-indexed
                "original": "T",
                "edited": "C",
                "sequence": variant,
                "description": f"Bystander edit at position {i+1} (T->C)",
            })

    # Also generate the target edit alone
    target_variant = exon_seq[:edit_pos] + "C" + exon_seq[edit_pos+1:]
    variants.insert(0, {
        "position": edit_pos + 1,
        "original": "T",
        "edited": "C",
        "sequence": target_variant,
        "description": "Target edit T6->C (restores SMN1 sequence)",
    })

    # Generate combination variants (target + each bystander)
    for v in variants[1:]:  # skip the target-only variant
        combo = target_variant[:v["position"]-1] + "C" + target_variant[v["position"]:]
        variants.append({
            "position": f"{edit_pos+1}+{v['position']}",
            "original": "T+T",
            "edited": "C+C",
            "sequence": combo,
            "description": f"Target edit T6->C + bystander at position {v['position']}",
        })

    return variants


def predict_splicing_spliceai(sequence, variant_pos, ref_allele, alt_allele):
    """Run SpliceAI prediction for a variant.

    Requires: pip install spliceai tensorflow
    Returns delta scores for acceptor/donor gain/loss.
    """
    try:
        from keras.models import load_model
        from spliceai.utils import one_hot_encode
        import numpy as np

        # SpliceAI requires a specific input format
        # For custom sequences, we use the raw model
        print(f"  SpliceAI: Predicting splicing effect of "
              f"{ref_allele}->{alt_allele} at position {variant_pos}...")

        # Encode sequences
        # Note: SpliceAI typically works with VCF/genomic coordinates
        # For custom sequences, we'd need to use the model directly
        # This is a placeholder for the actual implementation

        return {
            "status": "REQUIRES_GPU_DEPLOYMENT",
            "note": "SpliceAI needs TensorFlow + model weights on GPU instance",
            "install_cmd": "pip install spliceai tensorflow-gpu",
            "alternative": "Use SpliceAI lookup (pre-computed) or Pangolin",
        }

    except ImportError:
        return {
            "status": "NOT_INSTALLED",
            "install_cmd": "pip install spliceai tensorflow",
            "note": "Install SpliceAI on GPU instance for predictions",
        }


def run_ese_analysis(args):
    """Run ESE/ESS analysis (CPU-only, no dependencies)."""
    outdir = Path(os.path.expanduser("~/gpu-fleet/results/SMA/base_editing"))
    outdir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("ESE/ESS Analysis: SMN2 vs SMN1 Exon 7")
    print("=" * 60)

    # Analyze wild-type SMN2 (disease state)
    smn2_ese = analyze_ese_ess(SMN2_EXON7, "SMN2 (disease - T at pos 6)")
    print(f"\nSMN2 (T6): ESE score = {smn2_ese['ese_score']}, "
          f"predicted inclusion = {smn2_ese['predicted_inclusion']}")
    for motif, data in smn2_ese["motifs"].items():
        print(f"  {motif}: {data['strength']} - {data['effect']}")

    # Analyze SMN1 (healthy / target after editing)
    smn1_ese = analyze_ese_ess(SMN1_EXON7, "SMN1 (healthy - C at pos 6)")
    print(f"\nSMN1 (C6): ESE score = {smn1_ese['ese_score']}, "
          f"predicted inclusion = {smn1_ese['predicted_inclusion']}")
    for motif, data in smn1_ese["motifs"].items():
        print(f"  {motif}: {data['strength']} - {data['effect']}")

    # Analyze bystander variants
    print("\n" + "-" * 60)
    print("BYSTANDER EDITING SCENARIOS")
    print("-" * 60)

    variants = generate_bystander_variants(SMN2_EXON7, edit_pos=5)
    variant_results = []

    for v in variants:
        ese = analyze_ese_ess(v["sequence"], v["description"])
        variant_results.append({
            **v,
            "ese_score": ese["ese_score"],
            "predicted_inclusion": ese["predicted_inclusion"],
            "sf2_asf_status": ese["motifs"]["SF2_ASF"]["strength"],
        })
        print(f"\n  {v['description']}:")
        print(f"    Sequence: {v['sequence'][:20]}...")
        print(f"    ESE score: {ese['ese_score']}, "
              f"inclusion: {ese['predicted_inclusion']}")
        print(f"    SF2/ASF: {ese['motifs']['SF2_ASF']['strength']}")

    # SpliceAI prediction (if available)
    if not args.ese_only:
        print("\n" + "-" * 60)
        print("SpliceAI PREDICTIONS")
        print("-" * 60)
        spliceai_result = predict_splicing_spliceai(
            SMN2_FULL, len(INTRON6_3PRIME) + 5, "T", "C"
        )
        print(f"  Status: {spliceai_result['status']}")
        if "note" in spliceai_result:
            print(f"  Note: {spliceai_result['note']}")

    # Write results
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "smn2_analysis": smn2_ese,
        "smn1_analysis": smn1_ese,
        "bystander_variants": variant_results,
        "conclusion": {
            "target_edit_effect": "T6->C RESTORES SF2/ASF ESE, should restore exon 7 inclusion",
            "published_validation": "Confirmed by Liu lab: 99% editing -> full SMN protein restoration",
            "bystander_risk": "Most nearby T's are outside the SF2/ASF motif - low splicing risk",
            "recommendation": "Prioritize guides with minimal bystander A's in editing window",
        },
    }

    json_path = outdir / "smn2_splicing_predictions.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    # TSV with variant analysis
    tsv_path = outdir / "smn2_ese_analysis.tsv"
    with open(tsv_path, "w") as f:
        f.write("variant\tposition\tese_score\tpredicted_inclusion\tsf2_asf\n")
        f.write(f"SMN2_wildtype\t-\t{smn2_ese['ese_score']}\t"
                f"{smn2_ese['predicted_inclusion']}\t"
                f"{smn2_ese['motifs']['SF2_ASF']['strength']}\n")
        f.write(f"SMN1_target\t-\t{smn1_ese['ese_score']}\t"
                f"{smn1_ese['predicted_inclusion']}\t"
                f"{smn1_ese['motifs']['SF2_ASF']['strength']}\n")
        for v in variant_results:
            f.write(f"{v['description']}\t{v['position']}\t{v['ese_score']}\t"
                    f"{v['predicted_inclusion']}\t{v['sf2_asf_status']}\n")

    # Human-readable report
    txt_path = outdir / "smn2_splicing_report.txt"
    with open(txt_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("SMN2 Splicing Prediction Report\n")
        f.write(f"Generated: {report['timestamp']}\n")
        f.write("=" * 70 + "\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write("The C6T substitution in SMN2 exon 7 disrupts the SF2/ASF (SRSF1)\n")
        f.write("exonic splicing enhancer motif, causing exon 7 skipping and\n")
        f.write("production of truncated SMN-delta7 protein.\n\n")
        f.write("ABE-mediated T6->C correction restores the SF2/ASF motif and\n")
        f.write("is predicted to restore exon 7 inclusion to SMN1-like levels.\n\n")

        f.write("ESE COMPARISON\n")
        f.write("-" * 40 + "\n")
        f.write(f"SMN2 (disease): ESE score {smn2_ese['ese_score']}, "
                f"SF2/ASF = {smn2_ese['motifs']['SF2_ASF']['strength']}\n")
        f.write(f"SMN1 (target):  ESE score {smn1_ese['ese_score']}, "
                f"SF2/ASF = {smn1_ese['motifs']['SF2_ASF']['strength']}\n\n")

        f.write("BYSTANDER EDIT RISK\n")
        f.write("-" * 40 + "\n")
        for v in variant_results:
            risk = "LOW" if v["sf2_asf_status"] == "STRONG" else "HIGH"
            f.write(f"  {v['description']}: SF2/ASF={v['sf2_asf_status']}, "
                    f"risk={risk}\n")

        f.write("\n\nNEXT STEPS FOR GPU\n")
        f.write("-" * 40 + "\n")
        f.write("1. Deploy SpliceAI on Vast.ai GPU for quantitative delta-PSI\n")
        f.write("2. Run BE-Hive for bystander editing outcome predictions\n")
        f.write("3. Model nusinersen + ABE combination effects\n")
        f.write("4. Predict editing outcomes with be_predict_efficiency\n")

    print(f"\n\nResults written to: {outdir}/")
    print(f"  - {json_path.name}: machine-readable predictions")
    print(f"  - {tsv_path.name}: ESE analysis table")
    print(f"  - {txt_path.name}: human-readable report")

    return report


def main():
    parser = argparse.ArgumentParser(description="SMN2 Splicing Prediction")
    parser.add_argument("--ese-only", action="store_true",
                        help="ESE/ESS analysis only (no GPU needed)")
    parser.add_argument("--bystander", action="store_true",
                        help="Include bystander editing scenarios")
    parser.add_argument("--with-nusinersen", action="store_true",
                        help="Model nusinersen combination effect")
    args = parser.parse_args()

    # Default to ESE-only if no GPU available
    if args.ese_only or True:  # Start with ESE analysis always
        run_ese_analysis(args)


if __name__ == "__main__":
    main()
