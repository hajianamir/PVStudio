"""Idempotent Offline-First Sync Service with Per-Field Auditable Conflict Logging."""

import datetime
import uuid
from typing import Dict, Any, List, Set
from app.schemas.mobile import SyncBatchRequest, SyncBatchResponse, FieldInspectionRecord, ConflictLogEntry

class MobileSyncService:
    def __init__(self):
        self._processed_sequences: Set[str] = set()
        self._db_store: Dict[str, FieldInspectionRecord] = {}
        self._conflict_logs: List[ConflictLogEntry] = []

    def process_sync_batch(self, batch: SyncBatchRequest) -> SyncBatchResponse:
        """Processes offline batch with strict sequence idempotency and per-field conflict logging."""
        if batch.sync_sequence_id in self._processed_sequences:
            return SyncBatchResponse(
                sync_sequence_id=batch.sync_sequence_id,
                status="SUCCESS",
                processed_count=len(batch.records),
                server_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )

        processed = 0
        batch_conflicts = []

        for record in batch.records:
            if record.record_id in self._db_store:
                existing = self._db_store[record.record_id]

                # Per-field comparison & conflict detection
                # 1. Checklist Answers Additive Union & Conflict Audit
                for k, v in record.checklist_answers.items():
                    if k in existing.checklist_answers and existing.checklist_answers[k] != v:
                        conflict = ConflictLogEntry(
                            conflict_id=str(uuid.uuid4()),
                            record_id=record.record_id,
                            field_name=f"checklist_answers.{k}",
                            existing_value=existing.checklist_answers[k],
                            incoming_value=v,
                            existing_updated_by=existing.inspector_id,
                            existing_updated_at=existing.timestamp_utc,
                            incoming_updated_by=record.inspector_id,
                            incoming_updated_at=record.timestamp_utc,
                            resolution_status="AUDITED_OVERWRITE" if record.timestamp_utc >= existing.timestamp_utc else "EXISTING_RETAINED"
                        )
                        self._conflict_logs.append(conflict)
                        batch_conflicts.append(conflict)

                # 2. Additive Merge for Scanned Barcodes (preserves all unique scans)
                merged_barcodes = sorted(list(set(existing.scanned_barcodes + record.scanned_barcodes)))
                record.scanned_barcodes = merged_barcodes

                # 3. Insulation Resistance Check
                if abs(record.insulation_resistance_mohm - existing.insulation_resistance_mohm) > 1e-3:
                    conflict = ConflictLogEntry(
                        conflict_id=str(uuid.uuid4()),
                        record_id=record.record_id,
                        field_name="insulation_resistance_mohm",
                        existing_value=existing.insulation_resistance_mohm,
                        incoming_value=record.insulation_resistance_mohm,
                        existing_updated_by=existing.inspector_id,
                        existing_updated_at=existing.timestamp_utc,
                        incoming_updated_by=record.inspector_id,
                        incoming_updated_at=record.timestamp_utc,
                        resolution_status="AUDITED_OVERWRITE" if record.timestamp_utc >= existing.timestamp_utc else "EXISTING_RETAINED"
                    )
                    self._conflict_logs.append(conflict)
                    batch_conflicts.append(conflict)

                if record.timestamp_utc >= existing.timestamp_utc:
                    self._db_store[record.record_id] = record
            else:
                self._db_store[record.record_id] = record

            processed += 1

        self._processed_sequences.add(batch.sync_sequence_id)

        return SyncBatchResponse(
            sync_sequence_id=batch.sync_sequence_id,
            status="SUCCESS" if not batch_conflicts else "CONFLICT_AUDITED",
            processed_count=processed,
            conflict_log_entries=batch_conflicts,
            server_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
