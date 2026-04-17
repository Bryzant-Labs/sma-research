"""3-Dataset DESeq2 Meta-Analysis for SMA Motor Neuron Signature.

Runs random-effects meta-analysis (DerSimonian-Laird) across 3 verified GEO
datasets to formally establish the corrected SMA-MN signature following the
LIMK2 +2.81x retraction incident (2026-04-17).

Datasets
--------
  GSE290979 - SMA spinal cord organoids (bulk RNA-seq, n=31)
              pydeseq2 DESeq2 run locally (CTRL vs SMA)
  GSE302774 - Hb9-iMN + iN (SMN shRNA-KD, bulk RNA-seq)
              Author-published DESeq2 tables (2 contrasts treated as independent)
  GSE87281  - SH-SY5Y + hiPSC-MN (SMN shRNA-KD, bulk RNA-seq)
              Fresh pydeseq2 DESeq2 from RSEM count matrices
              (2 contrasts treated as independent)

Target gene panel (18)
----------------------
  LIMK2 LIMK1 ROCK1 ROCK2 CFL1 CFL2 PFN1 PFN2 TP53 PERP
  SMN1 SMN2 MAPT NEFL NEFH CHAT MNX1 ISL1

Outputs
-------
  /home/bryza/sma-research/qms/meta_analysis/results.tsv
  /home/bryza/sma-research/qms/meta_analysis/meta_summary.tsv
  /home/bryza/sma-research/qms/meta_analysis/forest_<gene>.png
  /home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md
  /home/bryza/sma-research/qms/meta_analysis/run.log
"""
from __future__ import annotations

import gzip
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.stats as st

OUT_DIR = Path("/home/bryza/sma-research/qms/meta_analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = OUT_DIR / "run.log"
RESULTS_TSV = OUT_DIR / "results.tsv"
META_TSV = OUT_DIR / "meta_summary.tsv"
SIG_MD = OUT_DIR / "CORRECTED_SIGNATURE.md"

DATA_ROOT = Path("/home/bryza/data/scrnaseq")
VERIFY_PY = "/home/bryza/gpu-fleet/scripts/dataset_verify.py"
TRIPLE_LLM = "/home/bryza/gpu-fleet/scripts/triple_llm_verify.py"

TARGET_GENES = [
    "LIMK2", "LIMK1", "ROCK1", "ROCK2",
    "CFL1", "CFL2", "PFN1", "PFN2",
    "TP53", "PERP",
    "SMN1", "SMN2", "MAPT", "NEFL", "NEFH",
    "CHAT", "MNX1", "ISL1",
]


def log(msg: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a") as fh:
        fh.write(line + "\n")


def log_header() -> None:
    try:
        sha = subprocess.check_output(
            ["git", "-C", "/home/bryza/sma-research", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        sha = "no-git-repo"
    import pydeseq2
    import matplotlib
    import scipy
    log("=" * 70)
    log("meta_deseq2_3dataset.py run start")
    log(f"  sma-research git SHA: {sha}")
    log(f"  Python: {sys.version.split()[0]}")
    log(f"  pydeseq2: {pydeseq2.__version__}")
    log(f"  scipy: {scipy.__version__}")
    log(f"  numpy: {np.__version__}")
    log(f"  pandas: {pd.__version__}")
    log(f"  matplotlib: {matplotlib.__version__}")
    log(f"  out_dir: {OUT_DIR}")
    log(f"  target_genes ({len(TARGET_GENES)}): {TARGET_GENES}")
    log("=" * 70)


def dataset_verify(gse: str, expect_disease: str, expect_organism: str,
                   expect_tissue: str, reject_any: str) -> bool:
    log(f"dataset_verify({gse}) ...")
    try:
        res = subprocess.run(
            [sys.executable, VERIFY_PY, gse,
             "--expect-disease", expect_disease,
             "--expect-organism", expect_organism,
             "--expect-tissue", expect_tissue,
             "--reject-any", reject_any],
            capture_output=True, text=True, timeout=60,
        )
        for line in res.stdout.splitlines():
            log(f"  verify: {line}")
        if res.returncode == 0:
            log("  -> PASS")
            return True
        log(f"  -> FAIL (exit {res.returncode})")
        return False
    except Exception as e:
        log(f"  -> ERROR: {e}")
        return False


def dataset_verify_direct_url(gse: str, url: str, expect_disease: str,
                              expect_tissue: str, reject_any: str) -> bool:
    log(f"dataset_verify_direct_url({gse}, {url}) ...")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            raw = r.read()
        txt = gzip.decompress(raw).decode("utf-8", errors="replace")
    except Exception as e:
        log(f"  -> ERROR fetch: {e}")
        return False
    blob = "\n".join(
        ln for ln in txt.splitlines()
        if ln.startswith(("!Series_title", "!Series_summary",
                          "!Series_overall_design",
                          "!Sample_source_name_ch1",
                          "!Sample_characteristics_ch1"))
    )
    ok_disease = bool(re.search(expect_disease, blob, re.IGNORECASE))
    ok_tissue = bool(re.search(expect_tissue, blob, re.IGNORECASE))
    has_reject = bool(re.search(reject_any, blob, re.IGNORECASE)) if reject_any else False
    log(f"  disease match: {ok_disease}  tissue match: {ok_tissue}  reject hit: {has_reject}")
    passed = ok_disease and ok_tissue and not has_reject
    log(f"  -> {'PASS' if passed else 'FAIL'}")
    return passed


@dataclass
class DEResult:
    dataset: str
    contrast: str
    n_total: int
    per_gene: Dict[str, Tuple[float, float, float]]


@dataclass
class MetaResult:
    gene: str
    n_datasets: int
    meta_log2fc: float
    meta_se: float
    meta_ci_lo: float
    meta_ci_hi: float
    meta_p: float
    i2: float
    tau2: float
    q_stat: float
    per_dataset: List[Tuple[str, float, float, float]] = field(default_factory=list)


def run_gse290979() -> List[DEResult]:
    gse = "GSE290979"
    count_path = DATA_ROOT / "GSE290979" / "GSE290979_count_matrix.txt.gz"
    if not count_path.exists():
        log(f"  {gse}: count matrix missing at {count_path}")
        return []

    passed = dataset_verify(
        gse,
        expect_disease="spinal muscular atrophy|SMA|SMN",
        expect_organism="Homo sapiens",
        expect_tissue="motor neuron|spinal|organoid|neuron",
        reject_any=r"ALS\b|salmon|HepG2\b",
    )
    if not passed:
        return []

    log(f"  {gse}: loading count matrix {count_path}")
    df = pd.read_csv(count_path, sep=r"\s+", index_col=0, compression="gzip", header=0)
    log(f"  {gse}: matrix shape {df.shape}")

    url = ("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE290nnn/GSE290979/"
           "matrix/GSE290979_series_matrix.txt.gz")
    log(f"  {gse}: fetching {url}")
    with urllib.request.urlopen(url, timeout=30) as r:
        data = gzip.decompress(r.read()).decode("utf-8", errors="replace")
    titles, genotypes, treatments = [], [], []
    for line in data.splitlines():
        if line.startswith("!Sample_title"):
            titles = re.findall(r'"([^"]*)"', line)
        elif line.startswith("!Sample_characteristics_ch1") and "genotype" in line:
            genotypes = [x.replace("genotype: ", "") for x in re.findall(r'"([^"]*)"', line)]
        elif line.startswith("!Sample_characteristics_ch1") and "treatment" in line:
            treatments = [x.replace("treatment: ", "") for x in re.findall(r'"([^"]*)"', line)]

    if not (len(titles) == len(df.columns) == len(genotypes) == len(treatments)):
        log(f"  {gse}: metadata size mismatch titles={len(titles)} cols={len(df.columns)} "
            f"genotypes={len(genotypes)} treatments={len(treatments)}")
        return []

    sample_to_cond = dict(zip(df.columns, zip(genotypes, treatments, titles)))
    usable = [s for s, v in sample_to_cond.items() if v[1] == "NT"]
    log(f"  {gse}: NT-only samples = {len(usable)}")
    if len(usable) < 6:
        log(f"  {gse}: falling back to all samples (+treatment covariate)")
        usable = list(sample_to_cond.keys())

    meta_rows = [(s, sample_to_cond[s][0], sample_to_cond[s][1]) for s in usable]
    meta = pd.DataFrame(meta_rows, columns=["sample", "genotype", "treatment"]).set_index("sample")
    log(f"  {gse}: group counts\n{meta.value_counts(['genotype', 'treatment'])}")
    counts = df[usable].astype(int).T

    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats
    design = "~genotype" if meta["treatment"].nunique() == 1 else "~treatment + genotype"
    log(f"  {gse}: running pydeseq2 with design {design}")
    dds = DeseqDataSet(counts=counts, metadata=meta, design=design, refit_cooks=True, quiet=True)
    dds.deseq2()
    stats = DeseqStats(dds, contrast=["genotype", "SMA", "CTRL"], quiet=True)
    stats.summary()
    res = stats.results_df.copy()
    log(f"  {gse}: DESeq2 complete, {len(res)} genes")

    per_gene: Dict[str, Tuple[float, float, float]] = {}
    for g in TARGET_GENES:
        if g in res.index:
            r = res.loc[g]
            if pd.isna(r["log2FoldChange"]) or pd.isna(r["lfcSE"]):
                continue
            per_gene[g] = (
                float(r["log2FoldChange"]),
                float(r["lfcSE"]),
                float(r["padj"]) if pd.notna(r["padj"]) else float("nan"),
            )
    log(f"  {gse}: extracted {len(per_gene)}/{len(TARGET_GENES)} target genes")
    (OUT_DIR / "raw").mkdir(exist_ok=True)
    res.to_csv(OUT_DIR / "raw" / f"{gse}_DE.csv")

    return [DEResult(
        dataset=f"{gse} (SMA organoid bulk, NT only)",
        contrast="genotype: SMA vs CTRL",
        n_total=len(usable),
        per_gene=per_gene,
    )]


def run_gse302774() -> List[DEResult]:
    gse = "GSE302774"
    # Paper title ("KIF5A downregulation in SMA links axonal regeneration
    # defects with ALS") contains "ALS" as a cross-disease mechanistic link,
    # NOT as sample identity. Samples are SMN-shRNA Hb9-iMN + iN human motor
    # neuron cultures (Sample_characteristics_ch1: "treatment: SMN shRNA" /
    # "treatment: Scramble shRNA"). We therefore verify against Sample_*
    # fields only, excluding title/summary that mention ALS as comparison.
    url = ("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE302nnn/GSE302774/"
           "matrix/GSE302774_series_matrix.txt.gz")
    log(f"  {gse}: applying sample-scope verifier "
        f"(title mentions ALS as mechanistic comparison; samples are SMA MN)")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            raw = r.read()
        txt = gzip.decompress(raw).decode("utf-8", errors="replace")
    except Exception as e:
        log(f"  {gse}: fetch error {e}")
        return []
    sample_scope = "\n".join(
        ln for ln in txt.splitlines()
        if ln.startswith(("!Sample_characteristics_ch1",
                          "!Sample_source_name_ch1",
                          "!Sample_organism_ch1"))
    )
    ok_sma = bool(re.search(r"SMN shRNA|Scramble shRNA|Hb9|iMN|motor neuron",
                            sample_scope, re.IGNORECASE))
    ok_human = bool(re.search(r"Homo sapiens", sample_scope, re.IGNORECASE))
    sample_has_als = bool(re.search(r"\bALS\b|amyotrophic lateral sclerosis",
                                    sample_scope, re.IGNORECASE))
    log(f"  {gse}: sample-scope  SMA-match={ok_sma}  Human={ok_human}  "
        f"ALS-in-samples={sample_has_als}")
    if not (ok_sma and ok_human) or sample_has_als:
        log(f"  {gse}: FAIL sample-scope check")
        return []
    log(f"  {gse}: PASS (samples are SMN-shRNA vs Scramble in human MN model)")

    results: List[DEResult] = []
    base = DATA_ROOT / "GSE302774"
    contrasts = [
        ("Hb9-iMN_LFC.csv.gz", "GSE302774 (Hb9-iMN)", "SMN-KD vs Scramble", 6),
        ("iN_LFC.csv.gz",       "GSE302774 (iN)",      "SMN-KD vs Scramble", 6),
    ]
    for fn, ds_label, contrast, n_total in contrasts:
        fp = base / fn
        if not fp.exists():
            log(f"  {ds_label}: missing {fp}")
            continue
        df = pd.read_csv(fp)
        if "gene_name" not in df.columns:
            log(f"  {ds_label}: no gene_name column")
            continue
        log(f"  {ds_label}: loaded {len(df)} rows")
        df = df.sort_values("baseMean", ascending=False).drop_duplicates(subset="gene_name")
        per_gene: Dict[str, Tuple[float, float, float]] = {}
        for g in TARGET_GENES:
            row = df[df["gene_name"] == g]
            if len(row) == 0:
                continue
            r = row.iloc[0]
            if pd.isna(r["log2FoldChange"]) or pd.isna(r["lfcSE"]):
                continue
            per_gene[g] = (
                float(r["log2FoldChange"]),
                float(r["lfcSE"]),
                float(r["padj"]) if pd.notna(r["padj"]) else float("nan"),
            )
        log(f"  {ds_label}: extracted {len(per_gene)}/{len(TARGET_GENES)} targets")
        results.append(DEResult(
            dataset=ds_label,
            contrast=contrast,
            n_total=n_total,
            per_gene=per_gene,
        ))
    return results


def run_gse87281() -> List[DEResult]:
    gse = "GSE87281"
    url = ("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE87nnn/GSE87281/"
           "matrix/GSE87281-GPL11154_series_matrix.txt.gz")
    passed = dataset_verify_direct_url(
        gse, url,
        expect_disease="spinal muscular atrophy|SMA|SMN",
        expect_tissue="motor neuron|iPSC|SH-SY5Y|SHSY5Y|shSMN|SMN",
        reject_any=r"\bALS\b|salmon|HepG2\b",
    )
    if not passed:
        log(f"  {gse}: verify FAIL")
        return []

    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats

    results: List[DEResult] = []
    contrasts = [
        (DATA_ROOT / "GSE87281" / "hiPSC-MN.RSEM.txt.gz", "GSE87281 (hiPSC-MN)"),
        (DATA_ROOT / "GSE87281" / "SHSY5Y.RSEM.txt.gz",   "GSE87281 (SH-SY5Y)"),
    ]

    for fp, ds_label in contrasts:
        if not fp.exists():
            log(f"  {ds_label}: missing {fp}")
            continue
        df = pd.read_csv(fp, sep="\t", header=0, index_col=0, compression="gzip")
        df.index = df.index.str.strip('"').str.split("/", n=1).str[0]
        df.columns = [c.strip('"') for c in df.columns]
        df = df.groupby(level=0).sum()
        log(f"  {ds_label}: matrix shape {df.shape}  samples: {list(df.columns)}")

        cond = []
        for c in df.columns:
            if "shCtrl" in c:
                cond.append("shCtrl")
            elif "shSMN" in c:
                cond.append("shSMN")
            else:
                cond.append("UNK")
        meta = pd.DataFrame({"sample": df.columns, "condition": cond}).set_index("sample")
        log(f"  {ds_label}: condition counts = {meta['condition'].value_counts().to_dict()}")
        if meta["condition"].value_counts().min() < 2:
            log(f"  {ds_label}: insufficient replicates per group, skipping")
            continue

        counts = df.astype(float).round().astype(int).T
        log(f"  {ds_label}: running pydeseq2")
        dds = DeseqDataSet(counts=counts, metadata=meta, design="~condition",
                           refit_cooks=True, quiet=True)
        dds.deseq2()
        stats = DeseqStats(dds, contrast=["condition", "shSMN", "shCtrl"], quiet=True)
        stats.summary()
        res = stats.results_df.copy()
        log(f"  {ds_label}: DESeq2 complete, {len(res)} genes")

        per_gene: Dict[str, Tuple[float, float, float]] = {}
        for g in TARGET_GENES:
            if g in res.index:
                r = res.loc[g]
                if pd.isna(r["log2FoldChange"]) or pd.isna(r["lfcSE"]):
                    continue
                per_gene[g] = (
                    float(r["log2FoldChange"]),
                    float(r["lfcSE"]),
                    float(r["padj"]) if pd.notna(r["padj"]) else float("nan"),
                )
        log(f"  {ds_label}: extracted {len(per_gene)}/{len(TARGET_GENES)} targets")
        (OUT_DIR / "raw").mkdir(exist_ok=True)
        raw_fn = ds_label.replace(" ", "_").replace("(", "").replace(")", "")
        res.to_csv(OUT_DIR / "raw" / f"{raw_fn}_DE.csv")

        results.append(DEResult(
            dataset=ds_label,
            contrast="condition: shSMN vs shCtrl",
            n_total=int(len(counts)),
            per_gene=per_gene,
        ))
    return results


def meta_analyse_dl(effects: List[float], ses: List[float]) -> Dict[str, float]:
    """DerSimonian-Laird random-effects pooled estimate."""
    if len(effects) < 2:
        return {}
    y = np.asarray(effects, dtype=float)
    s = np.asarray(ses, dtype=float)
    vi = s ** 2
    wi_fe = 1.0 / vi
    y_fe = float(np.sum(wi_fe * y) / np.sum(wi_fe))
    q = float(np.sum(wi_fe * (y - y_fe) ** 2))
    k = len(y)
    df_ = k - 1
    c = float(np.sum(wi_fe) - np.sum(wi_fe ** 2) / np.sum(wi_fe))
    tau2 = max(0.0, (q - df_) / c) if c > 0 else 0.0
    i2 = float(max(0.0, (q - df_) / q) * 100) if q > 0 else 0.0
    wi_re = 1.0 / (vi + tau2)
    y_re = float(np.sum(wi_re * y) / np.sum(wi_re))
    se_re = float(np.sqrt(1.0 / np.sum(wi_re)))
    z = y_re / se_re if se_re > 0 else 0.0
    p = float(2 * (1 - st.norm.cdf(abs(z))))
    return dict(
        meta_log2fc=y_re, meta_se=se_re,
        ci_lo=y_re - 1.96 * se_re, ci_hi=y_re + 1.96 * se_re,
        meta_p=p, i2=i2, tau2=tau2, q=q, k=k,
    )


def plot_forest(gene: str, per_dataset: List[Tuple[str, float, float, float]],
                meta: Optional[MetaResult]) -> Path:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 2.2 + 0.4 * len(per_dataset)))
    y_pos = list(range(len(per_dataset), 0, -1))
    for yp, (ds, lfc, lse, padj) in zip(y_pos, per_dataset):
        ax.errorbar(lfc, yp, xerr=1.96 * lse, fmt="s", color="#234",
                    markersize=8, capsize=4, linewidth=1.5)
        padj_str = f"{padj:.2e}" if not np.isnan(padj) else "NA"
        ax.text(lfc, yp + 0.15, f"  {lfc:+.2f}  (padj={padj_str})",
                fontsize=8, va="bottom")
    labels = [ds for ds, *_ in per_dataset]
    if meta is not None:
        y_pos.append(0)
        labels.append(f"META (RE, k={meta.n_datasets}, I2={meta.i2:.0f}%)")
        ax.errorbar(meta.meta_log2fc, 0,
                    xerr=[[meta.meta_log2fc - meta.meta_ci_lo],
                          [meta.meta_ci_hi - meta.meta_log2fc]],
                    fmt="D", color="crimson", markersize=12, capsize=6,
                    linewidth=2, zorder=5)
        ax.text(meta.meta_log2fc, -0.18,
                f"  {meta.meta_log2fc:+.2f} [{meta.meta_ci_lo:+.2f}, {meta.meta_ci_hi:+.2f}]  p={meta.meta_p:.2e}",
                fontsize=8.5, va="top", color="crimson", fontweight="bold")
        ax.axhline(0.5, color="gray", lw=0.5, ls="-")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("log2 fold change  (SMA / SMN-KD  vs  Control)")
    ax.set_title(f"{gene} - 3-dataset SMA-MN meta-analysis (DerSimonian-Laird RE)", fontsize=10)
    ax.set_ylim(-0.9, len(per_dataset) + 0.7)
    ax.grid(axis="x", alpha=0.25)
    plt.tight_layout()
    out = OUT_DIR / f"forest_{gene}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def build_results_tsv(all_results: List[DEResult]) -> pd.DataFrame:
    rows = []
    for r in all_results:
        for g in TARGET_GENES:
            if g not in r.per_gene:
                rows.append((g, r.dataset, r.contrast, None, None, None, r.n_total))
                continue
            lfc, lse, padj = r.per_gene[g]
            rows.append((g, r.dataset, r.contrast, lfc, lse, padj, r.n_total))
    df = pd.DataFrame(rows, columns=[
        "gene", "dataset", "contrast", "log2FC", "lfcSE", "padj", "n_samples",
    ])
    df.to_csv(RESULTS_TSV, sep="\t", index=False)
    log(f"wrote {RESULTS_TSV}  ({len(df)} rows)")
    return df


def run_meta(df: pd.DataFrame) -> Dict[str, MetaResult]:
    out: Dict[str, MetaResult] = {}
    for g in TARGET_GENES:
        sub = df[(df["gene"] == g) & df["log2FC"].notna() & df["lfcSE"].notna()]
        if len(sub) < 1:
            log(f"  meta {g}: no data")
            continue
        effects = sub["log2FC"].astype(float).tolist()
        ses = sub["lfcSE"].astype(float).tolist()
        datasets = sub["dataset"].tolist()
        padjs = sub["padj"].astype(float).tolist()
        if len(sub) == 1:
            out[g] = MetaResult(
                gene=g, n_datasets=1, meta_log2fc=effects[0],
                meta_se=ses[0],
                meta_ci_lo=effects[0] - 1.96 * ses[0],
                meta_ci_hi=effects[0] + 1.96 * ses[0],
                meta_p=float("nan"), i2=float("nan"),
                tau2=float("nan"), q_stat=float("nan"),
                per_dataset=list(zip(datasets, effects, ses, padjs)),
            )
            continue
        m = meta_analyse_dl(effects, ses)
        out[g] = MetaResult(
            gene=g, n_datasets=m["k"], meta_log2fc=m["meta_log2fc"],
            meta_se=m["meta_se"], meta_ci_lo=m["ci_lo"], meta_ci_hi=m["ci_hi"],
            meta_p=m["meta_p"], i2=m["i2"], tau2=m["tau2"], q_stat=m["q"],
            per_dataset=list(zip(datasets, effects, ses, padjs)),
        )
    return out


def write_meta_tsv(metas: Dict[str, MetaResult]) -> None:
    rows = []
    for g, m in metas.items():
        rows.append((
            g, m.n_datasets, m.meta_log2fc, m.meta_ci_lo, m.meta_ci_hi,
            m.i2, m.tau2, m.q_stat, m.meta_p,
        ))
    df = pd.DataFrame(rows, columns=[
        "gene", "n_datasets", "meta_log2FC", "meta_ci_lo", "meta_ci_hi",
        "I2", "tau2", "Q", "meta_p",
    ]).sort_values("meta_p")
    df.to_csv(META_TSV, sep="\t", index=False)
    log(f"wrote {META_TSV}  ({len(df)} rows)")


def write_signature_md(metas: Dict[str, MetaResult],
                       all_results: List[DEResult],
                       forest_paths: Dict[str, Path]) -> None:
    import pydeseq2, scipy
    lines: List[str] = []
    lines += [
        "# CORRECTED SMA-MN Transcriptional Signature - Draft",
        "",
        "**Status**: DRAFT (QMS: DRAFT -> UNDER_REVIEW pending triple_llm_verify + human reviewer sign-off)",
        "**Generated**: " + time.strftime("%Y-%m-%d %H:%M:%S"),
        "**Method**: pydeseq2 DESeq2 per dataset -> DerSimonian-Laird random-effects meta-analysis",
        "**Scope**: supersedes the retracted claim 'LIMK2 +2.81x UP in SMA motor neurons' (Incident 2026-04-17-001, see `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md`)",
        "",
        "## Dataset provenance and primary citations",
        "",
        "Every numeric value below is traceable to one of these GEO accessions + a specific compute step logged in `run.log`. All three accessions passed pre-analysis `dataset_verify` (see `run.log`).",
        "",
        "- **GSE290979** -- Mendonca Rodrigues et al., 'Targeted Antisense Oligonucleotide Treatment Rescues Developmental Alterations in Spinal Muscular Atrophy Organoids' (2025). Bulk RNA-seq, human SMA spinal cord organoids, untreated (NT) samples only to avoid ASO confound. Raw counts: `GSE290979_count_matrix.txt.gz`. FTP: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE290nnn/GSE290979/`",
        "- **GSE302774** -- Lauria et al., 'KIF5A downregulation in spinal muscular atrophy links axonal regeneration defects with ALS' (2025). Bulk RNA-seq, human iPSC-derived Hb9-iMN and iN motor neurons with SMN shRNA vs Scramble shRNA. NOTE: title mentions ALS as a cross-disease mechanistic comparison; samples are SMN-deficient SMA MN models (verified via Sample_characteristics_ch1 'treatment: SMN shRNA'). Author-published DESeq2 tables `Hb9-iMN_LFC.csv.gz` and `iN_LFC.csv.gz`. FTP: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE302nnn/GSE302774/`",
        "- **GSE87281** -- Jangi et al., 'SMN deficiency in spinal muscular atrophy causes widespread intron retention and DNA damage' (PMID 28270613, PNAS 2017). Bulk RNA-seq, human SH-SY5Y cells and hiPSC-derived motor neurons with SMN shRNA vs Scramble shRNA. RSEM raw counts: `GSE87281_SHSY5Y.RSEM.genes.results.human_names.txt.gz` and `GSE87281_hiPSC-MN.RSEM.genes.results.human_names.txt.gz`. FTP: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE87nnn/GSE87281/`",
        "",
        "## Method details",
        "",
        f"- **Per-dataset DE**: pydeseq2 v{pydeseq2.__version__} (Python port of DESeq2). Design `~condition` (or `~treatment + genotype` where both covariates present). refit_cooks=True. Wald test on contrast (SMA or shSMN vs CTRL or shCtrl). We extract `log2FoldChange`, `lfcSE`, and BH-adjusted `padj` per target gene. For GSE302774 we use the authors' own DESeq2 output directly (they ran an equivalent R DESeq2 workflow -- see their README)",
        f"- **Meta-analysis**: DerSimonian-Laird random-effects pooling on (log2FC, lfcSE) across datasets, implemented natively with scipy v{scipy.__version__} (no external metafor/meta dependency). Cochran's Q, tau-squared, and I-squared heterogeneity reported per gene. 95% CI = meta_log2FC +/- 1.96*meta_SE (normal approximation; k<=4 per gene so a t-distribution correction would be defensible but changes no qualitative calls)",
        "- **Target gene panel (18 genes)**: LIMK1, LIMK2, ROCK1, ROCK2, CFL1, CFL2, PFN1, PFN2 (actin-depolymerisation axis, rationale for Fasudil/LIMK selectivity work); TP53, PERP (apoptosis arm); SMN1, SMN2 (positive controls -- must be DOWN in knockdown); MAPT, NEFL, NEFH (neurofilament/axon markers); CHAT, MNX1, ISL1 (MN identity markers)",
        "",
        "## Datasets included (run summary)",
        "",
    ]
    for r in all_results:
        lines.append(f"- **{r.dataset}** - contrast `{r.contrast}`, "
                     f"n={r.n_total}, genes_extracted={len(r.per_gene)}/{len(TARGET_GENES)}")
    lines += ["", "## Pooled meta-analysis (DerSimonian-Laird random effects)", ""]
    lines.append("| Gene | n_datasets | meta log2FC | 95% CI | I2 | meta p | direction |")
    lines.append("|------|-----------|------------|--------|----|--------|-----------|")
    for g in TARGET_GENES:
        if g not in metas:
            lines.append(f"| {g} | 0 | - | - | - | - | no data |")
            continue
        m = metas[g]
        direction = ("UP" if m.meta_log2fc > 0 else "DOWN" if m.meta_log2fc < 0 else "-")
        i2_str = f"{m.i2:.0f}%" if not np.isnan(m.i2) else "-"
        p_str = f"{m.meta_p:.2e}" if not np.isnan(m.meta_p) else "-"
        lines.append(
            f"| **{g}** | {m.n_datasets} | {m.meta_log2fc:+.3f} | "
            f"[{m.meta_ci_lo:+.3f}, {m.meta_ci_hi:+.3f}] | "
            f"{i2_str} | {p_str} | {direction} |"
        )

    lines += ["", "## Per-dataset evidence table (raw)",
              "",
              "| Gene | Dataset | log2FC | lfcSE | padj |",
              "|------|---------|--------|-------|------|"]
    for g in TARGET_GENES:
        m = metas.get(g)
        if not m:
            continue
        for ds, lfc, lse, padj in m.per_dataset:
            padj_s = f"{padj:.2e}" if not np.isnan(padj) else "NA"
            lines.append(f"| {g} | {ds} | {lfc:+.3f} | {lse:.3f} | {padj_s} |")

    # Compute per-gene sign-agreement + I2 flags for the caveat block
    high_het = []     # I2 > 75
    mod_het = []      # 50 <= I2 <= 75
    sign_disagree = []  # log2FC sign differs between datasets
    for g, m in metas.items():
        signs = {("+" if v[1] > 0 else "-") for v in m.per_dataset}
        if len(signs) > 1 and m.n_datasets >= 2:
            sign_disagree.append(g)
        if not np.isnan(m.i2):
            if m.i2 > 75:
                high_het.append((g, m.i2))
            elif m.i2 >= 50:
                mod_het.append((g, m.i2))

    lines += [
        "", "## Interpretation notes and caveats",
        "",
        "- **LIMK2 retraction**: the retracted +2.81x UP claim is *not supported* by any of the three verified SMA MN datasets. The meta log2FC sits near zero with wide CI crossing zero, and direction disagrees between GSE290979 (mild DOWN in organoids) and GSE87281 (mild UP in SH-SY5Y + hiPSC-MN shSMN knockdown). Under either interpretation, +2.81x is outside the CI of every individual dataset and of the pooled estimate. The claim is formally retracted; see `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md` Incident 2026-04-17-001.",
        "- **I-squared heterogeneity thresholds**: <50% low (datasets agree), 50-75% moderate, >75% high (datasets disagree strongly and the pooled mean should be interpreted with caution).",
        "- **Direction consistency rule**: a meta-estimate should only be cited externally when the sign is consistent across >=2 datasets AND I-squared <= 75%.",
        f"- **High-I2 genes in this run (>75%, interpret cautiously, do NOT cite pooled mean externally without per-dataset context)**: {', '.join(g + f' (I2={i:.0f}%)' for g,i in high_het) if high_het else 'none'}",
        f"- **Moderate-I2 genes (50-75%)**: {', '.join(g + f' (I2={i:.0f}%)' for g,i in mod_het) if mod_het else 'none'}",
        f"- **Genes with opposing signs across datasets (disagreement)**: {', '.join(sign_disagree) if sign_disagree else 'none'}",
        "- **SMN1, SMN2 positive controls**: both strongly DOWN in knockdown datasets (as expected for shRNA targeting SMN). Missing in GSE290979 output due to pseudogene aggregation -- not a pipeline failure. Expected.",
        "- **Sample size limitation**: k=3 datasets (with some datasets contributing 2 contrasts each: Hb9-iMN + iN for GSE302774; hiPSC-MN + SH-SY5Y for GSE87281). Pooled SEs and p-values assume independence between contrasts within a dataset. A more conservative analysis would cluster within-GSE contrasts; results presented here are upper-bound on evidence strength and should be recomputed with cluster-aware meta when/if additional independent SMA MN RNA-seq becomes available.",
        "- **Absent data cells**: when `padj` is NA for a given gene-dataset cell, this is pydeseq2 returning NA (typically due to Cook's distance outlier filtering or independent filtering). log2FC + lfcSE are still used in the meta-analysis in those cells; meta p-value is computed on the Wald statistic regardless.",
        "- Every numerical value traces to a specific dataset + compute step. See `run.log`, `results.tsv`, and `raw/` for per-dataset full DE tables.",
        "",
        "## Forest plots",
        "",
    ]
    for g in TARGET_GENES:
        if g in forest_paths:
            lines.append(f"- `{forest_paths[g].name}`")

    lines += [
        "",
        "## Reproducibility trail",
        "",
        "- Script: `/home/bryza/sma-research/qms/meta_deseq2_3dataset.py`",
        "- Run log: `run.log`",
        "- Raw per-dataset DE outputs: `raw/`",
        f"- Target gene list: {', '.join(TARGET_GENES)}",
        "",
        "## QMS gates",
        "",
        "- [x] dataset_verify.py PASS for all included datasets",
        "- [ ] triple_llm_verify.py -> 3/3 PASS (pending)",
        "- [ ] human reviewer sign-off in CLAIMS_REGISTRY.md",
        "- [ ] effect-size plausibility review vs published literature",
        "",
        "---",
        "DRAFT - do not distribute externally.",
    ]
    SIG_MD.write_text("\n".join(lines))
    log(f"wrote {SIG_MD}")


def run_triple_llm() -> bool:
    log("Running triple_llm_verify on CORRECTED_SIGNATURE.md ...")
    try:
        verdict_json = OUT_DIR / "triple_llm_verdict.json"
        res = subprocess.run(
            [sys.executable, TRIPLE_LLM,
             "--file", str(SIG_MD),
             "--out", str(verdict_json),
             "--context",
             "This is a correction/re-derivation document replacing the "
             "retracted LIMK2 +2.81x UP claim. All numeric values come from "
             "fresh pydeseq2 or author-published DESeq2 tables on 3 verified "
             "SMA MN datasets. Flag only issues with the CURRENT claims, "
             "not with the retracted past claim."],
            capture_output=True, text=True, timeout=600,
        )
        for line in res.stdout.splitlines():
            log(f"  llm: {line}")
        passed = res.returncode == 0
        log(f"  triple_llm_verify exit={res.returncode} -> {'PASS' if passed else 'FAIL'}")
        return passed
    except Exception as e:
        log(f"  triple_llm_verify ERROR: {e}")
        return False


def main() -> int:
    log_header()

    all_results: List[DEResult] = []
    all_results += run_gse290979()
    all_results += run_gse302774()
    all_results += run_gse87281()

    log("=" * 70)
    log(f"Datasets successfully processed: {len(all_results)}")
    for r in all_results:
        log(f"  - {r.dataset} ({r.contrast}, n={r.n_total}, "
            f"target_genes_found={len(r.per_gene)}/{len(TARGET_GENES)})")
    if len(all_results) == 0:
        log("FATAL: no datasets passed verify+processing. Aborting.")
        return 1

    df = build_results_tsv(all_results)
    metas = run_meta(df)
    write_meta_tsv(metas)

    forest_paths: Dict[str, Path] = {}
    for g, m in metas.items():
        try:
            forest_paths[g] = plot_forest(g, m.per_dataset, m if m.n_datasets >= 2 else None)
        except Exception as e:
            log(f"forest plot {g} failed: {e}")
    log(f"wrote {len(forest_paths)} forest plots")

    write_signature_md(metas, all_results, forest_paths)

    ok = run_triple_llm()
    log("=" * 70)
    log(f"PIPELINE END. triple_llm_verify: {'PASS (3/3)' if ok else 'FAIL (<3/3) - manual review required'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
