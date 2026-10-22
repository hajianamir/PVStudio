# Phase 1 Acceptance Gate Evidence Package Manifest

```
Phase: Phase 1 — Residential MVP
Version: 1.0.0
Freeze Date: Sprint 6 Week 3
Status: FROZEN — Ready for Gate Review
```

---

## Artifacts Manifest (10/10 Gate Criteria Covered)

| Gate ID | Gate Criterion Name | Evidence Artifact Location / Verification File | Status |
| :--- | :--- | :--- | :--- |
| **G1** | **Workflow Speed (<30 min)** | `docs/specs/evidence/G1_timed_walkthrough_log.pdf` (John Smith, Apex Solar; 18 min 45 sec walkthrough) | **FROZEN** |
| **G2** | **10 Physics Benchmarks** | `tests/benchmarks/run_all.py` (B1–B9 annual $\le \pm 3\%$, monthly $\le \pm 5\%$; B10 string-window verified) | **FROZEN** |
| **G3** | **Provenance Envelope (100%)** | `tests/test_provenance.py` (4 rejection path tests: missing module, version, hash, unknown version) | **FROZEN** |
| **G4** | **Refusal Safeguard** | `tests/test_compliance_refusal.py` & `tests/test_pdf_watermark.py` (HTTP 403 & rendered header watermark) | **FROZEN** |
| **G5** | **Weather Metadata Stamp** | `tests/test_proposal_generator.py` (4 required fields + policy_applied + divergence_flagged printed in PDF) | **FROZEN** |
| **G6** | **Section Toggles & White-Label**| `tests/test_whitelabel_branding.py` & `docs/specs/evidence/G6_header_color_screenshot.png` (Apex Solar branding) | **FROZEN** |
| **G7** | **RTL Layout Architecture** | `tests/test_rtl_layout.py` (`app/ui/rtl_validator.py` static scanner 0 physical CSS violations) | **FROZEN** |
| **G8** | **Marketing Audit Clean** | `audit_marketing.py` (0 marketing buzzwords across codebase) | **FROZEN** |
| **G9** | **Catalog Data Integrity** | `calc/compliance/profiles/` & Catalog ingest audit (100% entries have verified source URLs + timestamps) | **FROZEN** |
| **G10** | **Off-Grid & Hybrid Paths** | `tests/test_benchmarks.py` & generated proposal PDFs for Case 7 (off-grid) and Case 8 (hybrid) | **FROZEN** |
