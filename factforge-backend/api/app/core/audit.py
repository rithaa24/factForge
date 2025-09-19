"""
Audit logging with HMAC signature verification
"""
import os
import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any
from .db import get_db_session

HMAC_KEY = os.getenv("HMAC_KEY", "replace_with_random_hex_key_32_chars_minimum")

def sign_payload(payload: Dict[str, Any]) -> str:
    """
    Compute HMAC signature for payload
    
    Args:
        payload: Dictionary to sign
        
    Returns:
        Hex-encoded HMAC signature
    """
    payload_json = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    signature = hmac.new(
        HMAC_KEY.encode(),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def create_audit_entry(event_type: str, payload: Dict[str, Any], db=None):
    """
    Create audit log entry with HMAC signature
    
    Args:
        event_type: Type of event (e.g., 'check', 'review', 'admin')
        payload: Event payload data
        db: Database session (optional)
    """
    signature = sign_payload(payload)
    
    if db:
        # Use provided session
        from .models import AuditLog
        audit_entry = AuditLog(
            event_type=event_type,
            payload=payload,
            signature=signature
        )
        db.add(audit_entry)
        db.commit()
    else:
        # Create new session
        with get_db_session() as db:
            from .models import AuditLog
            audit_entry = AuditLog(
                event_type=event_type,
                payload=payload,
                signature=signature
            )
            db.add(audit_entry)

def verify_audit_signature(audit_id: str) -> bool:
    """
    Verify HMAC signature for an audit entry
    
    Args:
        audit_id: UUID of audit entry
        
    Returns:
        True if signature is valid, False otherwise
    """
    with get_db_session() as db:
        from .models import AuditLog
        audit_entry = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
        
        if not audit_entry:
            return False
        
        # Recompute signature
        computed_signature = sign_payload(audit_entry.payload)
        
        # Compare signatures
        return hmac.compare_digest(audit_entry.signature, computed_signature)

def get_audit_entries(event_type: str = None, limit: int = 100, offset: int = 0):
    """
    Get audit entries with optional filtering
    
    Args:
        event_type: Filter by event type (optional)
        limit: Maximum number of entries to return
        offset: Number of entries to skip
        
    Returns:
        List of audit entries
    """
    with get_db_session() as db:
        from .models import AuditLog
        query = db.query(AuditLog)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

def cleanup_old_audit_logs(days: int = 365):
    """
    Clean up old audit logs (keep for compliance)
    
    Args:
        days: Number of days to retain logs
    """
    from datetime import timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    with get_db_session() as db:
        from .models import AuditLog
        deleted_count = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).delete()
        
        return deleted_count
