# RFdiffusion AAV9 Capsid Design

**Started**: 2026-04-10
**Status**: RUNNING (ETA ~22:00 UTC, 2026-04-10)
**Priority**: HIGH

## Goal

Design 50 AAV9 VP1 capsid variants with improved motor-neuron tropism for SMA gene therapy.

## Setup

- **Target**: AAV9 VP1
- **Contig**: `A219-489/10-25/A507-580/10-25/A598-736` (VR-V and VR-VIII loops)
- **GPU**: A100 PCIe 80 GB (Sweden), instance `34565416`
- **Compute**: ~2.5 h on A100

## Output destination

`2026-04-10_rfdiffusion/` — will contain:
- 50 generated VP1 backbones (`.pdb`)
- ProteinMPNN sequence designs
- ESMfold validation
- Comparison vs AAV9 baseline + AAV-PHP.eB benchmarks

## Status

Waiting for compute completion. Data will sync from `gpu-fleet/results/SMA/aav_capsid_design/` when the run finishes.
