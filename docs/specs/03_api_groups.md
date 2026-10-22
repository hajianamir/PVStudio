# 03: API Groups & Endpoint Contracts Specification

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Engineering | 2025-02-18 | Principal API Engineer |

---

## 3.1 Overview & Endpoint Structure

The PVStudio API is a type-safe, OpenAPI 3.1 compliant REST interface built with **FastAPI**. All calculation, project management, and equipment endpoints require bearer token authentication (JWT via Keycloak OIDC).

* **Rate Limiting Policy (C1):** Standard API tier = 100 req/min per user; Heavy calculation tier (`/api/v1/calc/*`) = 10 req/min per user with HTTP 429 `Retry-After` headers.

---

## 3.2 Endpoint Groups & Summary Table

### Group 1: Projects & Site Management (`/api/v1/projects`)

| Method | Path | Summary / Purpose | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/projects` | Create project & load segment UI context. | `ProjectCreateSchema` | `ProjectDetailSchema` |
| `GET` | `/api/v1/projects` | List projects filtered by segment/org. | Query params (`segment`, `page`) | `PaginatedProjectsSchema` |
| `POST` | `/api/v1/projects/{id}/site-capture` | Upload geospatial roof/site boundary. | GeoJSON FeatureCollection | `SiteCaptureResponseSchema` |
| `GET` | `/api/v1/projects/{id}/3d-tiles` | Get Cesium 3D Tileset / terrain URL. | None | `TilesetMetadataSchema` |

### Group 2: Layout & Equipment Sizing (`/api/v1/designs`)

| Method | Path | Summary / Purpose | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/designs/{id}/auto-stringing` | Execute DC string formation & inverter allocation. | `AutoStringingRequestSchema` | `StringLayoutSchema` |
| `POST` | `/api/v1/designs/{id}/recommend-architecture` | Trigger Central vs. String architecture auto-recommender. | `RecommenderInputSchema` | `ArchitectureRecommendationSchema` |
| `POST` | `/api/v1/designs/{id}/auto-mv-collection` | Propose MV bay count, transformer sizing & voltage level. | `MVCollectionRequestSchema` | `MVCollectionProposalSchema` |
| `POST` | `/api/v1/designs/{id}/signatures` | Submit digital PE review signature & approve revision (B4). | `DigitalSignatureRequestSchema` | `SignatureRecordSchema` |

### Group 3: Calculation Engine (`/api/v1/calc`)

| Method | Path | Summary / Purpose | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/calc/dc-sizing` | Calculate temperature-adjusted string voltages & sizing. | `DCSizingInputSchema` | `DCSizingOutputSchema` |
| `POST` | `/api/v1/calc/cable-schedule` | Size DC/AC cables, ampacity, and voltage drops. | `CableSizingInputSchema` | `CableScheduleSchema` |
| `POST` | `/api/v1/calc/earthing-lightning` | IEC 62305 lightning risk & earth rod network impedance. | `LightningEarthingInputSchema` | `LightningEarthingOutputSchema` |
| `POST` | `/api/v1/calc/yield-simulation` | Trigger 8760-hour yield simulation run. | `YieldSimRequestSchema` | `YieldSimResultSchema` |
| `POST` | `/api/v1/calc/bankability-monte-carlo` | Run 10,000-iteration Monte Carlo P50/P75/P90 simulation. | `MonteCarloRequestSchema` | `BankabilityReportSchema` |

### Group 4: Equipment Catalog (`/api/v1/catalog`)

| Method | Path | Summary / Purpose | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/catalog/pv-modules` | Search validated PV module datasheets. | Query params (`manufacturer`, `min_p_mp`) | `ListPVModulesSchema` |
| `POST` | `/api/v1/catalog/pv-modules` | Submit new equipment datasheet for admin validation. | `PVModuleCreateSchema` | `PVModuleCatalogSchema` |

### Group 5: Field Operations & Android Sync (`/api/v1/field-sync`)

| Method | Path | Summary / Purpose | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/field-sync/checklists` | Upload completed offline installation checklists. | `ChecklistSubmissionSchema` | `SyncAckSchema` |
| `POST` | `/api/v1/field-sync/photos` | Upload geotagged site photo with annotations. | Multipart `image/jpeg` + metadata | `MediaUploadResponseSchema` |
| `POST` | `/api/v1/field-sync/barcodes` | Batch upload scanned equipment serial barcodes. | `BarcodeBatchSchema` | `BarcodeValidationSchema` |

---

## 3.3 OpenAPI 3.1 Snippet Example

Below is a representative OpenAPI snippet for the Central vs. String Architecture Auto-Recommender endpoint:

```yaml
openapi: 3.1.0
info:
  title: PVStudio API
  version: 1.0.0
paths:
  /api/v1/designs/{id}/recommend-architecture:
    post:
      summary: Auto-recommend optimal inverter architecture (Central vs. String)
      operationId: recommendArchitecture
      tags:
        - Design Recommender
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RecommenderInputSchema'
      responses:
        '200':
          description: Successful architecture recommendation with LCOE & CAPEX deltas
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ArchitectureRecommendationSchema'
        '400':
          description: Invalid site constraints or capacity below minimum threshold

components:
  schemas:
    RecommenderInputSchema:
      type: object
      required:
        - plant_capacity_mw
        - terrain_slope_variance_deg
        - grid_interconnection_kv
      properties:
        plant_capacity_mw:
          type: number
          example: 25.5
        terrain_slope_variance_deg:
          type: number
          example: 8.2
        grid_interconnection_kv:
          type: number
          example: 33.0
        bess_integration_required:
          type: boolean
          default: false

    ArchitectureRecommendationSchema:
      type: object
      required:
        - recommended_architecture
        - confidence_score
        - central_lcoe_usd_mwh
        - string_lcoe_usd_mwh
        - capex_delta_percent
      properties:
        recommended_architecture:
          type: string
          enum: [CENTRAL_INVERTER, STRING_INVERTER]
          example: STRING_INVERTER
        confidence_score:
          type: number
          example: 0.92
        central_lcoe_usd_mwh:
          type: number
          example: 38.45
        string_lcoe_usd_mwh:
          type: number
          example: 36.10
        capex_delta_percent:
          type: number
          example: -3.2
        justification_notes:
          type: array
          items:
            type: string
          example:
            - "Steep terrain slope (> 5 deg) favors string inverters to minimize DC cable run lengths."
            - "Lower O&M downtime penalty for decentralized string architecture."
