# Phase 1 Acceptance Gate Evidence Package Manifest

```
Phase: Phase 1 — Residential MVP
Version: 1.0.0
Freeze Date: Sprint 6 Week 3
Status: FROZEN — Ready for Gate Review
Navigability Standard: < 2 min lookup target (Claim, File Path & Page, Verification Method, Owner)
```

---

## Artifacts Manifest Directory (10/10 Gate Criteria Covered)

| Gate ID | Gate Claim | Artifact Exact File Path & Location | Verification Method / Command | Responsible Owner |
| :--- | :--- | :--- | :--- | :--- |
| **G1** | Address $\rightarrow$ Proposal $<30$ min working time. | `docs/specs/evidence/G1_walkthrough.pdf` (Page 1) | Open PDF; check elapsed time (18 min 45 sec) & John Smith (Apex Solar) sign-off. | Product Manager |
| **G2** | All 10 benchmarks pass (B1–B9 yield, B10 string window). | `tests/benchmarks/run_all.py` | Run `python tests/benchmarks/run_all.py`; check per-case deltas vs PVsyst 7.4.2. | Lead PV Engineer |
| **G3** | 100% persisted calculation results carry envelope. | `tests/test_provenance.py` | Run `pytest tests/test_provenance.py`; verify 4 rejection paths pass. | Lead Backend Engineer |
| **G4** | Refusal-to-guess blocks incomplete profiles & watermarks PDF. | `tests/test_compliance_refusal.py` & `docs/specs/evidence/G4_watermark.pdf` | Run `pytest tests/test_compliance_refusal.py` & `pdftotext G4_watermark.pdf - \| grep OVERRIDE`. | Lead Compliance Engineer |
| **G5** | Weather metadata stamp printed in report PDF text layer. | `tests/test_proposal_generator.py` & `docs/specs/evidence/sample_proposal.pdf` (Page 1) | Run `pytest tests/test_proposal_generator.py`; check provider, vintage, resolution, override. | Lead Backend Engineer |
| **G6** | Section toggles & white-label branding functional in PDF. | `tests/test_whitelabel_branding.py` & `docs/specs/evidence/G6_branding_header.png` | Open `G6_branding_header.png`; confirm #1e40af color, logo, and sign-off. | UI/UX Architect |
| **G7** | RTL-ready layout with 0 physical CSS violations. | `tests/test_rtl_layout.py` | Run `pytest tests/test_rtl_layout.py`; verify static scanner output list. | UI/UX Architect |
| **G8** | 0 marketing buzzwords across codebase & templates. | `audit_marketing.py` | Run `python audit_marketing.py`; check 0 hits across all files. | Lead Architect |
| **G9** | 100% catalog entries have source URLs & timestamps. | `calc/compliance/profiles/` & Catalog ingest audit log | Open catalog log; verify source URL and validation timestamp for each entry. | Lead Data Architect |
| **G10** | Off-grid and hybrid end-to-end runs produce proposals. | `docs/specs/evidence/Case_7_Offgrid_Proposal.pdf` & `Case_8_Hybrid_Proposal.pdf` | Open `Case_7_Offgrid_Proposal.pdf` & `Case_8_Hybrid_Proposal.pdf`; check string + battery. | Lead PV Engineer |
