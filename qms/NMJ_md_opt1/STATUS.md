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
  - Solvation target: TIP3P-FB, 1.0 nm padding, 0.15 M NaCl, neutralised -> expected ~450-650 k atoms
- **Force field:** amber14-all.xml (ff14SB) + amber14/tip3pfb.xml
- **Integrator:** Langevin Middle, 4 fs timestep via HMR (hydrogen mass 4.0 amu), HBonds constraints, rigid waters
- **Production target:** 100 ns per replicate, 3 independent replicates (GPU 0/1/2), frames every 100 ps
- **Reserve (GPU 3-7):** (a) 13-chain full complex incl. MuSK kinase reference run, (b) metadynamics on AGRIN-LRP4 interface (collective variable = centre-of-mass distance + LRP4 beta-propeller tilt), (c) OpenFold2 NMJ validation if early-finish.

## 3. Compute plan

| Phase | Step | Target time | Status |
|---|---|---|---|
| A.1 | Strip MuSK kinase | 1 s | DONE (local, 2026-04-17) |
| A.2 | PDBFixer pH 7.4 | 30 s | DONE (local, 2026-04-17) |
| A.3 | Solvate + build System.xml | 10-20 min | **PIVOT 2026-04-17 23:31 UTC** — OpenMM `Modeller.addSolvent` stuck twice (1st on `addHydrogens`, patched; 2nd on `addSolvent` itself, 46 min, 100% CPU, `wchar=0`). Killed PID 2342. Replaced with `03_tleap_solvate.py` (AmberTools tleap `solvateBox` + OpenMM `AmberPrmtopFile.createSystem(hydrogenMass=4 amu)` + XML serialise). tleap is O(N) lattice-fill; no template matching hang. Running now in tmux `solvate` (pdb4amber at 852% CPU). |
| A.4 | Rsync prep/ to B200 | 2 min | DONE (14 MB transferred to ssh7.vast.ai:32540) |
| B.1 | Minimise (10 000 steps L-BFGS) | 15-30 min | PENDING |
| B.2 | NVT heat 10 -> 300 K (250 ps) | 30 min | PENDING |
| B.3 | NPT equilibration (1 ns, restraints on CA -> release) | 2 h | PENDING |
| C.1 | Production 100 ns x 3 replicates (4 fs HMR, GPU 0/1/2 in parallel) | ~24 h wall / ~48 GPU-h | PENDING |
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
- [x] **Pivot 2026-04-17 23:31 UTC:** Abandoned OpenMM Modeller.addSolvent path. New `03_tleap_solvate.py` uses AmberTools tleap (solvateBox + addIonsRand for 0.15 M NaCl neutralise) then loads the produced prmtop+inpcrd into OpenMM, applies HMR (`hydrogenMass=4 amu`) at `createSystem`, and serialises `nmj_12chain_system.xml`. Also writes `nmj_12chain_solvated.pdb` and `solvation_stats.json` (expected by auto_fire watcher). Expected wall: pdb4amber 1-3 min, tleap pass1 (count waters) 5-10 min, tleap pass2 (final build) 5-10 min, OpenMM createSystem on 500k atoms 2-5 min. Total ETA ~25 min. Learning file: `/home/bryza/.claude/projects/-home-bryza/memory/learning-openmm-addsolvent-too-slow-multichain.md`.
- [x] **Auto-fire dispatcher armed** (`/workspace/nmj_md/auto_fire_on_solvate.sh` in tmux session `auto_fire`). On solvation complete, will fire 3 parallel replicates in tmux sessions `rep0`/`rep1`/`rep2`: GPU 0/1/2, seeds 42/137/314. Each runs minimise -> NVT 250 ps -> NPT 1 ns -> 100 ns production. Expected wall-time ~16-24 h per replicate on a single B200 (B200 FP64/FP32 throughput ~2x H100, so 100 ns ~12-18 h for ~500 k atoms).

## 7. Next check-in

- **T+10 min:** SSH confirmed, env installed, prep rsynced, solvation launched [DONE]
- **T+30-60 min:** Solvation done, auto-fire dispatches 3 replicates, minimisation begins
- **T+90 min:** NVT heating on all 3 reps; replicate 0 enters NPT
- **T+6 h:** 3 replicates in production, ~10-20 ns each
- **T+24 h:** Final frames written, analysis complete, RESULTS.md DRAFT queued for triple-LLM

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

