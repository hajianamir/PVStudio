# Phase 4 Sprint 4 Mid-Point Engineering & Gate Criteria Draft (G31–G40)

**Document Version:** 1.0.0
**Date:** October 2026
**Status:** Draft for Gate Review Preparation

---

## 1. Phase 4 Acceptance Gate Criteria Table (G31–G40)

| Gate ID | Gate Name | Assertion Statement | Evidence Source / Artifact | Verification Mode |
|:-------:|:----------|:--------------------|:---------------------------|:-----------------:|
| **G31** | Android Offline Sync Idempotency | Sequence ID re-transmissions return `SUCCESS` without duplicate DB records | `tests/test_phase4_sprint1_deliverables.py::test_android_offline_mobile_sync_idempotency_and_conflict_logging` | Automated CI |
| **G32** | Auditable Conflict Logging | Field inspection checklist conflicts log `ConflictLogEntry` with server/mobile values | `tests/test_phase4_sprint1_deliverables.py::test_android_offline_mobile_sync_idempotency_and_conflict_logging` | Automated CI |
| **G33** | Dual-Measurement Retention | Conflicting IV curve & insulation readings preserve BOTH measurements with `requires_engineer_review=True` | `tests/test_phase4_sprint3_deliverables.py::test_dual_measurement_preservation_records` | Automated CI |
| **G34** | User-Facing Conflict Resolution | `/mobile/resolve-conflict` updates record checklist answers upon lead engineer signoff | `tests/test_phase4_sprint3_deliverables.py::test_mobile_resolve_conflict_endpoint_and_record_update` | Automated CI |
| **G35** | AI Copilot Seeded Error Benchmark | AI Copilot flags $\ge 80\%$ of seeded design errors with $100\%$ valid standard citations | `tests/test_phase4_sprint1_deliverables.py::test_ai_copilot_seeded_error_case_benchmark` | Automated CI |
| **G36** | Fabricated Standard Rejection | AI citation validator rejects unapproved standards (`IEEE 99999`) and non-existent profile keys | `tests/test_phase4_sprint1_deliverables.py::test_citation_validator_deep_rejection_guardrail` | Automated CI |
| **G37** | OpenAPI 3.1 Spec Schema | OpenAPI 3.1 spec includes `mobile_field`, `ai_copilot`, `calc`, `projects`, `catalog`, `reports` groups | `tests/test_phase4_sprint2_deliverables.py::test_openapi_schema_endpoint_groups_inclusion` | Automated CI |
| **G38** | Webhook HMAC SHA-256 Signing | Webhook event payloads signed with hex HMAC SHA-256 and reject tampered payloads | `tests/test_phase4_sprint3_deliverables.py::test_webhook_hmac_tamper_rejection` | Automated CI |
| **G39** | Android UI Conflict Resolution Dialog | `MobileConflictResolutionDialog.tsx` renders side-by-side card comparison & explicit radio selection | `app/ui/MobileConflictResolutionDialog.tsx` | MANUAL_REQUIRED (Lead Android Dev signoff) |
| **G40** | Zero Regression Baseline | 100% pass rate across Phase 1, Phase 2, and Phase 3 acceptance gate test suites | `tests/run_phase1_acceptance_gates.py` | Automated CI |

---

## 2. AI Copilot Expansion Target (Sprint 4)

- **Target:** Expand AI Copilot seeded error test suite from 10 to 20 parametrized cases covering protection relay miscoordination (ANSI 21/87T), DETC transformer tap setting mismatches, and multi-jurisdiction MENA-GCC voltage rules.
