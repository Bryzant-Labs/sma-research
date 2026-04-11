# AAV9 Capsid Design — RFdiffusion + ProteinMPNN (2026-04-10)

**Status**: COMPLETE
**Pipeline**: RFdiffusion (backbone) + ProteinMPNN (sequence)
**Target**: AAV9 VP1 capsid for improved motor neuron tropism (SMA gene therapy delivery)
**N designs**: 52

## Method

Loop-redesign of the variable regions VR-V (residues 490-506) and VR-VIII (residues 581-597) of the AAV9 VP1 capsid. These two loops sit at the receptor-binding interface and determine tropism in known engineered serotypes (AAV-PHP.eB, AAV9.45, etc.).

- **Contig**: `A219-489/10-25/A507-580/10-25/A598-736`
  - Fixed: capsid scaffold residues 219-489, 507-580, 598-736
  - Hallucinated: 10-25 residues replacing VR-V and VR-VIII each
- **Backbone diffusion**: RFdiffusion, 52 independent designs
- **Sequence design**: ProteinMPNN, 1 sequence per backbone (default temperature)
- **GPU**: A100 PCIe 80 GB (Sweden), instance `34565416`
- **Wall time**: ~2.5 h

## Files in this directory

- `design_config.json` — pipeline configuration (contig, model versions, hyperparameters)
- `design_summary.json` — manifest of all 52 designs with PDB sizes and MPNN sequence directory pointers
- `rfdiffusion_VR5_VR8_27.pdb` / `_29.pdb` / `_32.pdb` / `_36.pdb` / `_40.pdb` — top 5 designs by PDB file size (proxy for the largest, most complete loop redesigns)

## Where the full data lives

All 52 PDB backbones and ProteinMPNN sequence outputs are too large for git. They are mirrored on Dropbox:

- `Dropbox/SMA/open_data/aav_capsid_2026-04-10/` — 52 `.pdb` files + 52 `mpnn_rfdiffusion_VR5_VR8_*/` sequence directories

The on-cluster source: `~/gpu-fleet/results/SMA/aav_capsid_design_final/`.

## Role in the broader project

This is one leg of the three-component **Simon cure protocol**:

1. **ABE base editing** — convert SMN2 c.840 C>T to restore exon 7 (Liu lab platform, we extend)
2. **AAV9 motor-neuron-tropic delivery** — these 52 designs (this campaign)
3. **Fasudil / LIMK2 inhibitor** — reverses actin pathology in surviving motor neurons (Track 2B)

Down-stream validation pipeline (next campaign): rank designs by ESMfold pLDDT + receptor docking + retain top 5-10 for in vitro infection assays at a partner lab.

## Status & next steps

- [x] 52 designs generated
- [ ] ESMfold validation of redesigned loops (pLDDT > 70 cutoff)
- [ ] Top-10 selection for downstream cell-line testing
- [ ] Cryo-EM-quality renders of top 3 for figures

See parent `../README.md` for the full AAV capsid campaign context.
