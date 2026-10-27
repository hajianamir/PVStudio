import React, { useState } from 'react';

interface ConflictItem {
    conflict_id: string;
    record_id: string;
    field_name: str;
    existing_value: any;
    incoming_value: any;
    existing_updated_by: string;
    existing_updated_at: string;
    incoming_updated_by: string;
    incoming_updated_at: string;
}

interface MobileConflictResolutionDialogProps {
    conflict: ConflictItem;
    onResolved: (conflictId: string, chosenValue: any) => void;
    onCancel: () => void;
}

export const MobileConflictResolutionDialog: React.FC<MobileConflictResolutionDialogProps> = ({
    conflict,
    onResolved,
    onCancel,
}) => {
    const [selectedSource, setSelectedSource] = useState<'EXISTING' | 'INCOMING' | null>(null);
    const [resolutionNotes, setResolutionNotes] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleConfirm = async () => {
        if (!selectedSource) return;
        setSubmitting(true);

        const chosenValue = selectedSource === 'EXISTING' ? conflict.existing_value : conflict.incoming_value;

        try {
            const response = await fetch('/api/v1/mobile/resolve-conflict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conflict_id: conflict.conflict_id,
                    chosen_value: chosenValue,
                    resolved_by: 'lead_technician',
                    resolution_notes: resolutionNotes,
                }),
            });

            if (response.ok) {
                onResolved(conflict.conflict_id, chosenValue);
            }
        } catch (err) {
            console.error('Failed to resolve conflict:', err);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="conflict-dialog-backdrop" style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="conflict-dialog-card" style={{ backgroundColor: '#1e293b', color: '#f8fafc', padding: '24px', borderRadius: '12px', maxWidth: '500px', width: '100%' }}>
                <h3 style={{ margin: '0 0 16px 0', color: '#f59e0b' }}>⚠️ Inspection Field Conflict Resolution</h3>
                <p style={{ fontSize: '14px', color: '#94a3b8' }}>Field: <strong>{conflict.field_name}</strong></p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', margin: '16px 0' }}>
                    <div
                        onClick={() => setSelectedSource('EXISTING')}
                        style={{
                            padding: '12px',
                            borderRadius: '8px',
                            border: selectedSource === 'EXISTING' ? '2px solid #3b82f6' : '1px solid #334155',
                            backgroundColor: selectedSource === 'EXISTING' ? '#1e3a8a' : '#0f172a',
                            cursor: 'pointer',
                        }}
                    >
                        <span style={{ fontSize: '12px', color: '#64748b' }}>SERVER VALUE</span>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', margin: '4px 0' }}>{String(conflict.existing_value)}</div>
                        <div style={{ fontSize: '11px', color: '#94a3b8' }}>{conflict.existing_updated_by}</div>
                        <div style={{ fontSize: '10px', color: '#64748b' }}>{conflict.existing_updated_at}</div>
                    </div>

                    <div
                        onClick={() => setSelectedSource('INCOMING')}
                        style={{
                            padding: '12px',
                            borderRadius: '8px',
                            border: selectedSource === 'INCOMING' ? '2px solid #3b82f6' : '1px solid #334155',
                            backgroundColor: selectedSource === 'INCOMING' ? '#1e3a8a' : '#0f172a',
                            cursor: 'pointer',
                        }}
                    >
                        <span style={{ fontSize: '12px', color: '#64748b' }}>MOBILE VALUE</span>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', margin: '4px 0' }}>{String(conflict.incoming_value)}</div>
                        <div style={{ fontSize: '11px', color: '#94a3b8' }}>{conflict.incoming_updated_by}</div>
                        <div style={{ fontSize: '10px', color: '#64748b' }}>{conflict.incoming_updated_at}</div>
                    </div>
                </div>

                <textarea
                    placeholder="Resolution notes (required)..."
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', backgroundColor: '#0f172a', color: '#f8fafc', border: '1px solid #334155', margin: '8px 0 16px 0' }}
                />

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                    <button onClick={onCancel} style={{ padding: '8px 16px', borderRadius: '6px', backgroundColor: '#334155', color: '#f8fafc', border: 'none' }}>Cancel</button>
                    <button
                        onClick={handleConfirm}
                        disabled={!selectedSource || submitting}
                        style={{ padding: '8px 16px', borderRadius: '6px', backgroundColor: selectedSource ? '#2563eb' : '#475569', color: '#ffffff', border: 'none' }}
                    >
                        Confirm Resolution
                    </button>
                </div>
            </div>
        </div>
    );
};
