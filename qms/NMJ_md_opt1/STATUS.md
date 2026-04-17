# NMJ 100 ns MD — Option 1 STATUS

**Agent:** Opus NMJ-MD-Opt1 recovery  
**Started:** 2026-04-17 21:20 UTC  
**Last update:** 2026-04-17 23:31 UTC  
**Owner:** Opus fleet supervisor  
**Sibling task:** Opt 2 bispecific farm (Vast 35151592, 8x B200, separate agent)

---

## 1. Context and decision

- **Original plan:** Nebius H100 rental for Opt 1 NMJ MD (companion of `NMJ_bispecific_farm/HANDOFF_CHRISTIAN_NEBIUS_RENT_OPT2.md`, which covers Opt 2 only — no Opt 1 handoff existed).
- **Brev sma-nmj-md-opt1 (u6x7n9jp4):** reported FAILURE per `brev ls`. CLI was logged out (malformed refresh token); did not attempt `brev reset` because Christian meanwhile rented B200 capacity that supersedes the Brev box.
- **Handoff supersede:** Christian rented a dedicated 8x B200 on Vast — Contract 35152540, ssh7.vast.ai:32540, label `sma-nmj-md-opt1-b200-20260417`, 24 h cap (~$735). NO Nebius rental initiated. NO Brev recovery attempted past CLI login (would not have been the fastest path).
- **Sibling run:** Opt 2 (bispecific farm) lives on Vast 35151592, ssh4.vast.ai:31592, 8x B200 Ohio. Strictly isolated — no cross-ssh, no cross-tmux, no cross-mount.

## 2. System selection

With 8x B200 (1.47 TB VRAM aggregate, 2 TB system RAM, 500 GB NVMe) we move from "pick one sub-interface" to "run 3 independent replicates of the 12-chain ECD NMJ assembly in parallel + keep headroom for a 13-chain full-atom run on GPU 3+."

- **Primary system:** 12-chain NMJ ECD assembly
  - Source: `/home/bryza/sma-research/qms/NMJ_super_complex/assembly/nmj_super_complex.pdb` -> strip MuSK kinase chain H (+260 A lateral offset is a kludge) -> `nmj_12chain_ecd_stripped.pdb`
  - Chains retained: A C B D E F G I J K P Z (AChR alpha1 x2, AChR beta/delta/epsilon, RAPSN, MuSK ECD, DOK7, LRP4 ECD, AGRIN, PERP, H2b_9_s2 binder)
  - After PDBFixer (pH 7.4, side-chain completion, no cross-chain residue stitching): **12 chains, 8 084 residues, 123 137 atoms** (protein only, pre-solvation)
  - Solvation target: TIP3P, 1.0 nm padding, 0.15 M NaCl, neutralised -> **ACTUAL: 5 796 016 atoms** (dramatically larger than the initial 450-650 k guess — the NMJ assembly's elongated geometry drives a 514 × 380 × 317 A box with 292 k waters). **This means production MD will run at ~5-15 ns/day/replicate on B200, not 100 ns/day.** Protocol adjusted: finish equilibration + as much production as wall clock allows; Christian can rent longer if needed.
- **Force field:** amber14-all.xml (ff14SB) + amber14/tip3pfb.xml
- **Integrator:** Langevin Middle, 4 fs timestep via HMR (hydrogen mass 4.0 amu), HBonds constraints, rigid waters
- **Production target:** 100 ns per replicate, 3 independent replicates (GPU 0/1/2), frames every 100 ps
- **Reserve (GPU 3-7):** (a) 13-chain full complex incl. MuSK kinase reference run, (b) metadynamics on AGRIN-LRP4 interface (collective variable = centre-of-mass distance + LRP4 beta-propeller tilt), (c) OpenFold2 NMJ validation if early-finish.

## 3. Compute plan

| Phase | Step | Target time | Status |
|---|---|---|---|
| A.1 | Strip MuSK kinase | 1 s | DONE (local, 2026-04-17) |
| A.2 | PDBFixer pH 7.4 | 30 s | DONE (local, 2026-04-17) |
| A.3 | Solvate + build System.xml | 10-20 min | **DONE 2026-04-17 23:49 UTC** (tleap+OpenMM, wall 1076 s = 17.9 min). 5 796 016 atoms, 291 707 waters, 950 Na+ / 790 Cl-, protein net q = -160 neutralised. Files: `nmj_12chain.prmtop` (957 MB), `.inpcrd` (212 MB), `_solvated.pdb` (414 MB — **column-overflow due to 513 A box, unused**), `_system.xml` (1.4 GB, HMR 4 amu baked), `solvation_stats.json`. |
| A.3b | Patch 04/05 to load from prmtop+inpcrd (PDB column overflow at 1000+ A box) | 5 min | DONE |
| A.3c | Replace `minimizeEnergy` with restrained relaxation integration (OpenMM L-BFGS hits `std::vector::max_size()` above ~5 M atoms) | 5 min | DONE |
| A.4 | Rsync prep/ to B200 | 2 min | DONE (14 MB transferred to ssh7.vast.ai:32540) |
| B.1 | Relax 16 ps @ 10 K, dt 0.5 fs, k=50 kcal/mol/A^2 CA restraint (replaces L-BFGS) | 15-30 min wall on 5.8 M atoms | **RUNNING on GPU 0/1/2 (all 3 at 100% util, 4.9 GB each, 245-258 W) from 21:59 UTC** |
| B.2 | NVT heat 10 -> 300 K (250 ps, 2 fs, 10 kcal/mol/A^2 CA) | ~2 h wall | PENDING (follows B.1 in same process) |
| B.3 | NPT equilibration (1 ns, 4 fs HMR, k: 10 -> 2 -> 0) | ~4 h wall | PENDING |
| C.1 | Production MD (4 fs HMR, GPU 0/1/2 parallel) — expected **5-15 ns / day / replicate** on 5.8 M atoms (~3x slower than typical 500 k-atom systems). 21 h wall remaining -> realistic 10-30 ns per replicate, NOT 100 ns. If Christian extends rental -> full 100 ns possible in 7-14 days wall. | remaining 21 h wall | PENDING |
| D | prmtop from trajectory frame 0, MDAnalysis PBC-safe distance maps, RMSD/RMSF, interface contact analysis | 30 min | PENDING |
| E | Triple-LLM gate on RESULTS.md; DRAFT only | 10 min | PENDING |

## 4. Hard-rule compliance

- [x] POCKET_FIXED ligand placement (N/A — apo run)
- [ ] PBC-aware distance analysis (`box=u.dimensions`) — will enforce in analysis
- [ ] Amber prmtop built from trajectory frame 0 via `pdb4amber --no-reorder` (never from separate PDB)
- [ ] Verify `prmtop.atom_count == DCD.atom_count` before trusting analysis
- [x] Triple-LLM gate on RESULTS.md — queued
- [x] DRAFT only — Simon-Comms-Gate HELD
- [x] Never destroy B200 early — early-finish triggers replicate 4 and/or OpenFold2

## 5. Isolation from Opt 2 (sibling)

| | Opt 1 NMJ MD | Opt 2 Bispecific Farm |
|---|---|---|
| Vast instance | 35152540 | 35151592 |
| SSH | ssh7.vast.ai:32540 | ssh4.vast.ai:31592 |
| Label | sma-nmj-md-opt1-b200-20260417 | sma-bispecific-farm-b200-20260417 |
| Workspace | /workspace/nmj_md/ | /workspace/bispecific_farm/ |
| Owner agent | (this agent) | sibling agent |

No cross-ssh, no cross-tmux, no cross-mount. Agents communicate only via the Opus supervisor.

## 6. Blockers / open items

- [x] B200 SSH — opened ~60 s after launch. 8x B200 183 GB each, 500 GB NVMe, 2 TB RAM, Ubuntu 24.04 conda base.
- [x] conda env installed: openmm 8.1.2, pdbfixer, mdanalysis 2.10, ambertools 23, pdb4amber. 60 s wall.
- [x] Prep rsynced to /workspace/nmj_md/prep/ (12-chain stripped + fixed PDB + scripts).
- [x] **Pivot COMPLETE 2026-04-17 23:49 UTC.** Method = AmberTools tleap + OpenMM. Actual wall 17.9 min (pdb4amber 43 s + tleap pass 1 counting waters 5:47 + tleap pass 2 final 8:47 + OpenMM createSystem 35 s + XML serialise). System: 5 796 016 atoms (12-chain NMJ has elongated 514 × 380 × 317 A bounding box).
- [x] **Downstream script patches (B200-specific):**
  - `04_minimize_equilibrate.py` + `05_production.py` now load topology from `AmberPrmtopFile` and positions from `AmberInpcrdFile` (NOT `PDBFile`). tleap's savepdb overflows the 8-char coord column when any atom coord exceeds 999.999 A (our box is 513 A centered, extremes exceed the column width). Binary prmtop+inpcrd path is the standard large-system Amber workflow.
  - `04_minimize_equilibrate.py` stage 1 replaced `simulation.minimizeEnergy()` with 16 ps restrained relaxation (T=10 K, dt=0.5 fs, k=50 kcal/mol/A^2 on CA). OpenMM's LocalEnergyMinimizer (L-BFGS) throws `std::vector::max_size()` on > 5 M-atom systems due to history-buffer allocation. Relaxation integration is the accepted NAMD/GROMACS-style alternative.
  - Intermediate state writes (after relax / NVT / NPT) changed from `PDBFile.writeFile` -> `State XML` serialise (same PDB column-overflow reason).
- [x] **GPU utilisation target hit 2026-04-17 23:59 UTC.** GPU 0/1/2 all at 100% util, 4.9 GB VRAM each, 245-258 W draw. 3 B200s running independent replicates (seeds 42/137/314) in parallel. GPU 3-7 idle (kept as reserve for full 13-chain atomistic run or metadynamics add-on if Christian wants).
- [x] Learning file written: `/home/bryza/.claude/projects/-home-bryza/memory/learning-openmm-addsolvent-too-slow-multichain.md` (companion to `learning-openmm-addhydrogens-hang.md`). Linked from MEMORY.md.
- [x] **Auto-fire dispatcher armed** (`/workspace/nmj_md/auto_fire_on_solvate.sh` in tmux session `auto_fire`). On solvation complete, will fire 3 parallel replicates in tmux sessions `rep0`/`rep1`/`rep2`: GPU 0/1/2, seeds 42/137/314. Each runs minimise -> NVT 250 ps -> NPT 1 ns -> 100 ns production. Expected wall-time ~16-24 h per replicate on a single B200 (B200 FP64/FP32 throughput ~2x H100, so 100 ns ~12-18 h for ~500 k atoms).

## 7. Next check-in

- **T+10 min:** SSH confirmed, env installed, prep rsynced, solvation launched [DONE]
- **T+2 h 30 min:** OpenMM addSolvent stuck 46 min, killed, tleap pivot, System XML written 2026-04-17 23:49 UTC [DONE]
- **T+2 h 40 min:** auto_fire fired rep0/1/2, downstream patches iterated, GPU 0/1/2 at 100% 23:59 UTC [DONE]
- **T+3 h:** rep0 relaxation stage finishes, enters NVT heating
- **T+5 h:** NVT heat done on 3 reps, NPT equilibration begins
- **T+9 h:** NPT done, production starts (first NPT frame ~T+5 h, first production frame ~T+9 h)
- **T+24 h wall cap:** ~10-30 ns produced per replicate (5.8 M atoms is ~3x slower than 500 k-atom budget assumption). If needed, recommend rental extension.

## 8. Commands to inspect progress

```bash
# SSH to box
ssh -i ~/.ssh/id_ed25519_prestaging -p 32540 root@ssh7.vast.ai

# All MD logs
tail -f /workspace/nmj_md/logs/solvate_run.log
tail -f /workspace/nmj_md/logs/auto_fire.log
tail -f /workspace/nmj_md/logs/rep{0,1,2}_full.log

# Tmux sessions
tmux ls                # expect: solvate, auto_fire, rep0, rep1, rep2
tmux attach -t rep0    # detach with Ctrl-b d

# GPU utilisation
nvidia-smi
```

