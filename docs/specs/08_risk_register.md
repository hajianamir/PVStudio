# 08: Risk Register & Mitigation Matrix

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Engineering | 2025-02-18 | Chief Technology Officer |

---

## 8.1 Risk Evaluation Framework

Risks are categorized across Technical, Computational, Regulatory, Operational, and Financial vectors. Each risk is evaluated on a $1-5$ Likelihood ($L$) and $1-5$ Impact ($I$) scale, yielding a Risk Score ($R = L \times I$).

---

## 8.2 Technical Risk Register Table

| Risk ID | Risk Category & Description | $L$ | $I$ | Score | Mitigation Strategy | Risk Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TR-01** | **Calculation Engine Discrepancy vs. Industry Benchmarks:** Discrepancies between PVStudio yield outputs and legacy software (PVsyst/SAM). | 2 | 5 | **10 (High)** | Implement an automated benchmark regression test suite running 10 reference cases against PVsyst outputs. Enforce maximum allowable error threshold $\le 1.5\%$. | Lead Computational Engineer |
| **TR-02** | **3D Viewport Performance Degradation:** CesiumJS frame-rate drops when rendering $> 500,000$ PV modules in Utility-Scale plants. | 3 | 4 | **12 (High)** | Implement instanced mesh rendering in CesiumJS/R3F, level-of-detail (LOD) simplification, and bounding box culling for distant arrays. | Lead UI/UX Engineer |
| **TR-03** | **Mobile Field Data Sync Conflicts:** Offline field checklists overwrite concurrent cloud design changes upon re-establishing connection. | 3 | 3 | **9 (Med)** | Implement vector-clock / CRDT conflict resolution. Operational edits in the field are appended as event-sourced audit delta logs rather than direct table overwrites. | Lead Mobile Engineer |
| **TR-04** | **Regulatory Misinterpretation / Invalid Sizing:** System permits a non-compliant DC string sizing due to missing or outdated local grid code rules. | 2 | 5 | **10 (High)** | Enforce the **Refusal-to-Guess** safeguard. If a compliance profile is incomplete, block auto-approval and mandate qualified human PE sign-off. | Regulatory Lead |
| **TR-05** | **Monte Carlo Compute Bottlenecks:** $10,000$-iteration Monte Carlo yield simulations exhaust worker node RAM or exceed API timeouts. | 3 | 3 | **9 (Med)** | Offload heavy simulations to Celery worker clusters; vectorize calculation routines using NumPy/Numba; cache results by `input_hash`. | Lead Backend Architect |
| **TR-06** | **AI Copilot Hallucination:** AI design review module suggests non-standard electrical configurations or hallucinates standard citations. | 4 | 4 | **16 (Critical)** | Restrict AI Copilot to RAG (Retrieval-Augmented Generation) over validated YAML profiles and standard text documents. Mandate strict citation of standard clause numbers. | AI Lead |
