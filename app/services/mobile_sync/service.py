"""Idempotent Offline-First Sync Service with Auditable Conflict Resolution UI & Dual-Measurement Preservation."""

import datetime
import uuid
from typing import Dict, Any, List, Set
from app.schemas.mobile import (
    SyncBatchRequest,
    SyncBatchResponse,
    FieldInspectionRecord,
    ConflictLogEntry,
    DualMeasurementRecord,
    ConflictResolutionRequest
)

class MobileSyncService:
    def __init__(self):
        self._processed_sequences: Set[str] = set()
        self._db_store: Dict[str, FieldInspectionRecord] = {}
        self._conflict_logs: Dict[str, ConflictLogEntry] = {}
        self._dual_measurements: List[DualMeasurementRecord] = []

    def process_sync_batch(self, batch: SyncBatchRequest) -> SyncBatchResponse:
        """Processes offline batch with sequence idempotency, per-field conflict logging & dual-measurement preservation."""
        if batch.sync_sequence_id in self._processed_sequences:
            return SyncBatchResponse(
                sync_sequence_id=batch.sync_sequence_id,
                status="SUCCESS",
                processed_count=len(batch.records),
                server_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )

        processed = 0
        batch_conflicts = []
        batch_dual_measurements = []

        for record in batch.records:
            if record.record_id in self._db_store:
                existing = self._db_store[record.record_id]

                # 1. Checklist Answers Conflict Log (Surfaced to User-Facing Resolution UI)
                for k, v in record.checklist_answers.items():
                    if k in existing.checklist_answers and existing.checklist_answers[k] != v:
                        conflict_id = str(uuid.uuid4())
                        conflict = ConflictLogEntry(
                            conflict_id=conflict_id,
                            record_id=record.record_id,
                            field_name=f"checklist_answers.{k}",
                            existing_value=existing.checklist_answers[k],
                            incoming_value=v,
                            existing_updated_by=existing.inspector_id,
                            existing_updated_at=existing.timestamp_utc,
                            incoming_updated_by=record.inspector_id,
                            incoming_updated_at=record.timestamp_utc,
                            resolution_status="PENDING_HUMAN_RESOLUTION"
                        )
                        self._conflict_logs[conflict_id] = conflict
                        batch_conflicts.append(conflict)

                # 2. Additive Merge for Scanned Barcodes (preserves all unique scans)
                merged_barcodes = sorted(list(set(existing.scanned_barcodes + record.scanned_barcodes)))
                record.scanned_barcodes = merged_barcodes

                # 3. Dual-Measurement Preservation for Insulation Resistance (NEVER overwrites, preserves BOTH)
                if abs(record.insulation_resistance_mohm - existing.insulation_resistance_mohm) > 1e-3:
                    dual_rec = DualMeasurementRecord(
                        measurement_id=str(uuid.uuid4()),
                        record_id=record.record_id,
                        parameter_type="INSULATION_RESISTANCE",
                        reading_a={"insulation_resistance_mohm": existing.insulation_resistance_mohm},
                        reading_b={"insulation_resistance_mohm": record.insulation_resistance_mohm},
                        timestamp_a=existing.timestamp_utc,
                        timestamp_b=record.timestamp_utc,
                        technician_a=existing.inspector_id,
                        technician_b=record.inspector_id,
                        requires_engineer_review=True
                    )
                    self._dual_measurements.append(dual_rec)
                    batch_dual_measurements.append(dual_rec)
                    record.dual_measurements.append(dual_rec)

                # 4. Dual-Measurement Preservation for IV Curve Measurements
                if record.iv_curve_measurements and existing.iv_curve_measurements:
                    if record.iv_curve_measurements != existing.iv_curve_measurements:
                        dual_rec_iv = DualMeasurementRecord(
                            measurement_id=str(uuid.uuid4()),
                            record_id=record.record_id,
                            parameter_type="IV_CURVE",
                            reading_a={"iv_curve_points": existing.iv_curve_measurements},
                            reading_b={"iv_curve_points": record.iv_curve_measurements},
                            timestamp_a=existing.timestamp_utc,
                            timestamp_b=record.timestamp_utc,
                            technician_a=existing.inspector_id,
                            technician_b=record.inspector_id,
                            requires_engineer_review=True
                        )
                        self._dual_measurements.append(dual_rec_iv)
                        batch_dual_measurements.append(dual_rec_iv)
                        record.dual_measurements.append(dual_rec_iv)

                self._db_store[record.record_id] = record
            else:
                self._db_store[record.record_id] = record

            processed += 1

        self._processed_sequences.add(batch.sync_sequence_id)

        return SyncBatchResponse(
            sync_sequence_id=batch.sync_sequence_id,
            status="SUCCESS" if not batch_conflicts else "CONFLICT_PENDING_RESOLUTION",
            processed_count=processed,
            conflict_log_entries=batch_conflicts,
            dual_measurement_records=batch_dual_measurements,
            server_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

    def resolve_user_conflict(self, req: ConflictResolutionRequest) -> ConflictLogEntry:
        """User-facing resolution endpoint handler for resolving checklist conflicts."""
        if req.conflict_id not in self._conflict_logs:
            raise KeyError(f"Conflict ID {req.conflict_id} not found.")

        conflict = self._conflict_logs[req.conflict_id]
        conflict.resolution_status = "RESOLVED"

        # Update underlying record in store
        record = self._db_store.get(conflict.record_id)
        if record and conflict.field_name.startswith("checklist_answers."):
            key = conflict.field_name.split("checklist_answers.")[1]
            record.checklist_answers[key] = req.chosen_value

        return conflict
