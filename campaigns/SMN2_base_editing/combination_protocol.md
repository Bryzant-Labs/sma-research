# Combination Protocol: ABE Base Editing + Fasudil ROCK Inhibition for SMA

Version: 1.0
Date: 2026-04-08
Authors: Christian Fischer, Bryzant Labs
Status: Protocol Design (pre-experiment)

---

## 1. Rationale

### The Problem with Single-Agent Approaches

**Base editing alone** (ABE corrects SMN2 to SMN1):
- Fixes the root genetic cause: restores full-length SMN protein production
- Takes days to weeks for full therapeutic effect (viral transduction -> editing -> transcription -> protein accumulation)
- Does NOT repair already-damaged neuromuscular junctions (NMJs) or muscle fibers
- In delta7 SMA mice, ABE alone extends lifespan by ~33% (Arbab et al., Science 2023)

**Fasudil alone** (ROCK inhibitor):
- Immediately improves muscle function via ROCK-LIMK2-CFL2 pathway (hours to days)
- Addresses downstream actin cytoskeletal dysfunction in NMJs and muscle
- Does NOT fix the root cause (SMN protein deficiency persists)
- Transient benefit only -- requires continuous dosing

### The Combination Hypothesis

ABE + Fasudil could be synergistic because they operate on different timescales and different biological layers:

1. **ABE** = the cure. One-time genetic correction of SMN2, restoring SMN protein production permanently. But there is a critical "gap period" between injection and full therapeutic protein levels.

2. **Fasudil** = the bridge. During the gap period (days 0-14 after AAV-ABE injection), Fasudil provides immediate neuroprotection by:
   - Inhibiting ROCK -> reducing LIMK2 hyperphosphorylation -> normalizing cofilin (CFL2) activity
   - Improving actin dynamics at NMJs (the ROCK-LIMK2-CFL2 axis, validated in 3 independent SMA datasets)
   - Preventing further NMJ denervation while SMN protein levels are still rising

3. **Analogy**: Treating a bacterial infection with antibiotics (cure, takes days) PLUS anti-inflammatory drugs (immediate symptom relief). Neither alone is as good as the combination.

### Why This Combination is Novel
- The Liu lab (Science 2023) tested ABE + nusinersen combination and achieved the best result: 111-day lifespan in delta7 mice
- NOBODY has tested ABE + ROCK inhibitor
- ROCK-LIMK2-CFL2 is a therapeutic axis we identified across 3 independent SMA datasets
- Fasudil is generic, orally bioavailable, crosses BBB, and has extensive human safety data (approved in Japan/China for cerebral vasospasm)
- LIMK2-selective SMA therapy = ZERO global competitors

### Supporting Evidence for the ROCK Pathway in SMA
- Bowerman et al. (2012): ROCK pathway hyperactivated in SMA muscle -- Fasudil improves muscle function
- Our analysis: ROCK-LIMK2-CFL2 axis consistently dysregulated across SMA transcriptomic datasets
- CORO1C identified as passenger (NOT driver) -- the real target is LIMK2
- Fasudil acts on the muscle/NMJ side, which is mechanistically distinct from SMN protein restoration

---

## 2. Proposed Study Design

### Mouse Model

**Delta7-SMA mice** (B6.Cg-Tg(SMN2)89Ahmb Smn1tm1Msd Tg(SMN2*delta7)4299Ahmb/J)
- Jackson Labs #005025
- Genotype: Smn-/-; SMN2+/+; SMNdelta7+/+
- Median survival: ~13-15 days (untreated)
- Same model used by Arbab et al. (Science 2023)

### Treatment Groups

| Group | N | ABE (P0-P1) | Fasudil (P1-P14) | Purpose |
|-------|---|-------------|-------------------|---------|
| A: Combination | 15 | AAV9-ABE ICV 4e10 vg | 10 mg/kg/day IP | Test combination efficacy |
| B: ABE alone | 15 | AAV9-ABE ICV 4e10 vg | Vehicle IP | Base editing monotherapy control |
| C: Fasudil alone | 10 | AAV9-GFP ICV | 10 mg/kg/day IP | ROCK inhibitor monotherapy control |
| D: Vehicle | 10 | AAV9-GFP ICV | Vehicle IP | Negative control |
| E: Untreated | 10 | None | None | Natural history control |
| F: Heterozygous | 5 | None | None | Healthy control (Smn+/-) |

**Total mice: ~65**

### Treatment Protocol

#### Day P0-P1: Base Editing Injection
- **Agent**: Dual AAV9-intein-split ABE8e-SpRY + gRNA A8
- **Route**: Intracerebroventricular (ICV) injection, bilateral
- **Dose**: 4 x 10^10 vector genomes (vg) total, based on Arbab et al.
- **Volume**: 2 uL per lateral ventricle (4 uL total)
- **Timing**: Within 24 hours of birth (P0 or P1)

#### Days P1-P14: Fasudil Treatment
- **Agent**: Fasudil hydrochloride (HA-1077, Sigma #H139)
- **Route**: Intraperitoneal (IP) injection
- **Dose**: 10 mg/kg/day (based on Bowerman et al. 2012 SMA dosing)
- **Vehicle**: Sterile saline (0.9% NaCl)
- **Frequency**: Once daily
- **Duration**: P1 through P14 (critical window of SMA pathology)
- **Rationale for stopping at P14**: By this time, ABE-mediated SMN protein restoration should be approaching therapeutic levels

#### Dose Rationale
- Fasudil 10 mg/kg IP is well-tolerated in neonatal mice (Bowerman 2012)
- This dose inhibits ROCK sufficiently to normalize LIMK2 phosphorylation
- Higher doses (30 mg/kg) risk hypotension in neonates

### Endpoints

#### Primary Endpoints
| Endpoint | Method | Timepoints |
|----------|--------|------------|
| Survival | Daily monitoring | Continuous |
| Body weight | Daily weighing | P1-P60+ |
| Righting reflex | Time to right from supine | P5, P7, P9, P12, P14 |

#### Secondary Endpoints
| Endpoint | Method | Timepoints |
|----------|--------|------------|
| Grip strength | Grip test | P12, P21, P28, P42 |
| Rotarod | Accelerating rotarod | P21, P28, P42 |
| Hindlimb splay | Suspension test | P7, P14, P21 |

#### Molecular Endpoints (at sacrifice)
| Endpoint | Method | Tissue |
|----------|--------|--------|
| SMN2 editing efficiency | Amplicon deep sequencing | Spinal cord, brain, muscle |
| SMN protein levels | Western blot, ELISA | Spinal cord, brain, liver, muscle |
| Exon 7 inclusion | RT-qPCR | Spinal cord, muscle |
| LIMK2 phosphorylation | Western blot (p-LIMK2/total) | Spinal cord, muscle |
| CFL2 phosphorylation | Western blot (p-CFL2/total) | Spinal cord, muscle |
| NMJ morphology | IF (BTX + neurofilament) | Tibialis anterior, diaphragm |
| Motor neuron counts | ChAT immunostaining | Lumbar spinal cord L1-L5 |
| Muscle fiber size | H&E histology | TA, diaphragm, intercostal |

#### Safety Endpoints
| Endpoint | Method | Tissue |
|----------|--------|--------|
| Off-target editing | CHANGE-seq-BE | Spinal cord, liver |
| Bystander editing | Amplicon sequencing | Spinal cord |
| AAV biodistribution | qPCR | Multiple organs |
| Liver/kidney function | ALT, AST, BUN, creatinine | Serum |

---

## 3. Why the Combination Could Be Synergistic

### Temporal Complementarity

```
Day:    0    1    2    3    4    5    6    7   ...14   ...28  ...60+
ABE:    ICV  -    -    -    -    edit start    ~50%   ~80%   ~87%
        inj                      appearing     edit   edit   edit

Fasudil: -   IP   IP   IP   IP   IP   IP   IP  STOP
              |________________________________|
              Immediate ROCK inhibition during
              the critical "editing gap" window

SMN:    0%   0%   0%   ~5%  ~10% ~15% ~20% ~30%  ~60%  ~90%  ~95%
        |_____________________________|
        During this period, SMN is still LOW
        but Fasudil protects NMJs from damage
```

### Mechanistic Synergy

1. **ABE restores SMN protein** (upstream cause)
   - SMN is a spliceosome assembly factor
   - Full restoration takes 2-4 weeks post-injection
   - During the gap, motor neurons and NMJs continue to degenerate

2. **Fasudil protects during the gap** (downstream effect)
   - ROCK hyperactivation -> LIMK2 hyperphosphorylation -> CFL2 inactivation -> frozen actin dynamics
   - This causes NMJ retraction and muscle denervation
   - Fasudil immediately normalizes this pathway
   - Prevents irreversible NMJ loss during the critical P1-P14 window

3. **Together: fix the cause AND prevent damage during the fix**
   - Like treating a bacterial infection: antibiotics (cure, takes days) + anti-inflammatory (immediate relief)

### Predicted Outcome
- **Survival**: Combo group should exceed 111 days (the current ABE + nusinersen record)
- **Motor function**: Earlier and stronger improvement vs ABE alone
- **NMJ morphology**: Better preserved NMJs in combo group at P14-P21

---

## 4. Honest Risks and Mitigation

### Risk 1: Fasudil May Interfere with AAV9 Uptake
- **Mechanism**: ROCK is involved in endocytosis pathways; ROCK inhibition could theoretically reduce AAV9 cellular entry
- **Mitigation**: Start Fasudil at P1 (24h after AAV injection), allowing time for AAV9 uptake
- **Assessment**: LOW risk. AAV9 uses receptor-mediated endocytosis (AAVR receptor), which is ROCK-independent

### Risk 2: Timing Window is Critical
- Fasudil too early (P0, concurrent with AAV) might reduce editing efficiency
- Mitigation: Staggered start -- AAV at P0, Fasudil at P1
- Fasudil stopped too early might not bridge the full gap
- Mitigation: Continue through P14

### Risk 3: Dose Interactions
- Combined stress of ICV injection + daily IP injections on neonates
- Mitigation: Experienced neonatal mouse surgeons; monitor body temperature
- Contingency: If pup mortality high in first 48h, delay Fasudil start to P2

### Risk 4: Fasudil Hypotension in Neonates
- ROCK inhibition causes vasodilation; neonates are more susceptible
- 10 mg/kg is well-tolerated (Bowerman 2012)
- Contingency: Reduce to 5 mg/kg if side effects observed

### Risk 5: Interpreting Results
- Difficult to distinguish synergy from additivity
- Mitigation: Full factorial design with monotherapy controls
- Use Bliss independence model for synergy analysis
- N=15 per treatment group provides 80% power to detect 20% survival difference

---

## 5. Our Unique Contribution

### What Nobody Else Does
- ROCK-LIMK2-CFL2 therapeutic axis: identified across 3 independent SMA datasets
- Fasudil for SMA muscle: we understand the muscle-mediated (not neuroprotective) mechanism
- LIMK2-selective strategy: ZERO global competitors
- ABE + ROCK inhibitor combination: never proposed or tested

### Collaboration Potential
- **Liu Lab / Broad**: ABE constructs + ICV injection expertise
- **Sellier Lab / IGBMC**: European partner, guide optimization
- **Bowerman Lab**: Original Fasudil-SMA work, mouse model expertise
- **Bryzant Labs**: ROCK pathway biology, combination rationale, computational pipeline

### Why This Matters for Patients
- Current therapies are imperfect: Zolgensma has ceiling on SMN, nusinersen/risdiplam require lifelong dosing
- Base editing could be a true cure (one-time, endogenous regulation preserved)
- But editing alone leaves existing damage unrepaired
- **Our combination = cure + repair = best possible outcome**

---

## 6. Cost Estimate

| Item | Cost |
|------|------|
| Delta7 SMA mice (20 breeding pairs) | 4,000 EUR |
| AAV9-ABE dual vector (4 batches) | 12,000 EUR |
| AAV9-GFP control (2 batches) | 3,000 EUR |
| Fasudil hydrochloride | 1,000 EUR |
| Animal facility (30 cages x 3 months) | 4,500 EUR |
| Behavioral testing equipment | 500 EUR |
| Histology (80 samples) | 4,000 EUR |
| Western blots (60 blots) | 1,800 EUR |
| RT-qPCR (100 reactions) | 1,000 EUR |
| Amplicon deep sequencing (40 samples) | 4,000 EUR |
| Off-target analysis CHANGE-seq-BE (4 samples) | 8,000 EUR |
| Personnel (technician, 50% FTE, 4 months) | 8,000 EUR |
| Contingency (10%) | 5,180 EUR |
| **TOTAL** | **~57,000 EUR** |

Reducible to ~30-40K EUR if AAV vectors obtained through academic collaboration and off-target analysis deferred.

---

## 7. Timeline

| Month | Activity |
|-------|----------|
| M1 | Breed mice, order reagents, produce AAV vectors |
| M2 | Pilot study (N=3/group, confirm dosing/tolerability) |
| M3 | Main study begins (all groups) |
| M4 | Behavioral monitoring, survival curves |
| M5 | Sacrifice timepoints (P14, P28), tissue collection |
| M6 | Molecular analysis (sequencing, WB, histology) |
| M7 | Data analysis, manuscript preparation |
| M8 | Submit manuscript + preprint |

---

## 8. Expected Deliverables

1. Survival curves demonstrating combination superiority over monotherapies
2. Motor function data showing earlier functional recovery
3. Molecular evidence of SMN2 editing + ROCK pathway normalization
4. NMJ morphology data showing preserved innervation
5. Manuscript suitable for Nature Medicine / Science Translational Medicine
6. Provisional patent on ABE + ROCK inhibitor combination for SMA

---

## References

1. Arbab M et al. Science 380, eadg6518 (2023). PMID:36996170
2. Sellier C et al. Nat Biomed Eng 8(2):118-131 (2024). PMID:38057426
3. Bowerman M et al. BMC Med 10:24 (2012). PMID:22420665
4. Mendell JR et al. NEJM 377(18):1713-1722 (2017). PMID:29091557
5. Patent: WO2022150706A2
