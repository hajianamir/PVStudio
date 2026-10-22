# Phase 1 Specification: 3D Roof View Minimum Viable Scope (R3F)

```
Document Class: Derived Execution Document (3D Scope Freeze)
Subordinate To: PHASE_1_RESIDENTIAL_MVP.md & PVStudio_Technical_Product_Specification.md v1.0.0 (FROZEN)
Governance: Engineering-owned scope lock for Sprint 5 R3F 3D Implementation
```

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | LOCKED — Sprint 5 MVP Scope | 2025-02-18 | Lead 3D/Geospatial Engineer & UI/UX Architect |

---

## 1. Objective & Scope Freeze Mandate

This document locks the Minimum Viable Scope for the React Three Fiber (R3F) 3D Roof View in Phase 1 (Sprint 5). It prevents visual polish creep while delivering all necessary 3D spatial features to satisfy Gate Criterion G1 (address $\rightarrow$ proposal $< 30 \text{ min}$).

---

## 2. In-Scope R3F Features (Phase 1 Sprint 5 MVP)

| Feature Area | Minimum Viable Scope |
| :--- | :--- |
| **1. Roof Geometry Mesh** | Extruded 3D roof plane mesh generated directly from MapLibre 2D polygon boundaries, with pitch angle slider ($0^\circ - 60^\circ$) and azimuth orientation vector. |
| **2. Module Placement** | Grid array module placement over roof planes; drag-and-drop module repositioning; automatic boundary collision detection. |
| **3. Obstacle Bounding Mesh** | 3D bounding geometry rendering for tagged obstacles (chimneys, HVAC units, skylights) with keep-out buffer zones. |
| **4. Shading Heatmap Overlay** | Visual color heatmap (green $\rightarrow$ yellow $\rightarrow$ red) applied to module meshes representing annual shading derate percentage ($0\% - 30\%+$). |
| **5. Viewport Navigation** | OrbitControls (pan, zoom, rotate) with standard camera presets (Top 2D, Isometric 3D, South View). |

---

## 3. Explicitly Out-of-Scope Items (Deferred to Phase 2/3)

* Photorealistic PBR materials, glass reflections, and high-resolution roof shingle textures.
* Dynamic sun-path shadows animated in real-time across 8760 hours (shading is rendered as a pre-computed annual heatmap overlay).
* Architectural details beyond extruded roof planes (e.g. gutters, fascia, doors, windows, trees).
* Multi-building campus terrain rendering (CesiumJS terrain tiles reserved for C&I / Utility-Scale in Phase 2/3).

---

## 4. G1 Verification Criterion

For Phase 1 Gate G1 evidence, the 3D viewport MUST successfully display:
1. Extruded roof plane matching MapLibre capture
2. Modules placed in grid layout over roof plane
3. Chimney/HVAC obstacle box
4. Color-coded annual shading heatmap overlay on module meshes
