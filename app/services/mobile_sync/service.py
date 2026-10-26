"""Idempotent Offline-First Sync Service for Android Client Field Records."""

import datetime
from typing import Dict, Any, List, Set
from app.schemas.mobile import SyncBatchRequest, SyncBatchResponse, FieldInspectionRecord

class MobileSyncService:
    def __init__(self):
        self._processed_sequences: Set[str] = set()
        self._db_store: Dict[str, FieldInspectionRecord] = {}

    def process_sync_batch(self, batch: SyncBatchRequest) -> SyncBatchResponse:
        """Processes offline batch with strict idempotency and timestamp LWW conflict resolution."""
        # Idempotency check: if sequence ID already processed, return previous acknowledgment
        if batch.sync_sequence_id in self._processed_sequences:
            return SyncBatchResponse(
                sync_sequence_id=batch.sync_sequence_id,
                status="SUCCESS",
                processed_count=len(batch.records),
                server_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )

        processed = 0
        rejected = []

        for record in batch.records:
            # LWW (Last-Write-Wins) Conflict Resolution based on timestamp_utc
            if record.record_id in self._db_store:
                existing = self._db_store[record.record_id]
                if record.timestamp_utc >= existing.timestamp_utc:
                    self._db_store[record.record_id] = record
                    processed += 1
                else:
                    # Ignore older incoming record
                    rejected.append(record.record_id)
            else:
                self._db_store[record.record_id] = record
                processed += 1

        self._processed_sequences.add(batch.sync_sequence_id)

        return SyncBatchResponse(
            sync_sequence_id=batch.sync_sequence_id,
            status="SUCCESS" if not rejected else "CONFLICT_RESOLVED",
            processed_count=processed,
            rejected_records=rejected,
            server_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
