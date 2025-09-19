"""
Admin API endpoints
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import requests
import time

from ..core.db import get_db_session, get_redis
from ..core.auth import require_admin
from ..core.audit import create_audit_entry, verify_audit_signature
from ..core.models import User, CrawledItem, ReviewQueue, AuditLog, ModelVersion
from ...llm import get_llm_provider_info, switch_llm_provider

router = APIRouter()

class CrawlerStatus(BaseModel):
    is_running: bool
    last_run: Optional[str]
    urls_processed: int
    errors: int
    active_workers: int

class ModelUpdate(BaseModel):
    classifier_version: Optional[str] = None
    embedding_model: Optional[str] = None
    llm_version: Optional[str] = None
    thresholds: Optional[Dict[str, float]] = None
    is_active: bool = True

class SystemStats(BaseModel):
    total_users: int
    total_posts: int
    total_crawled_items: int
    pending_reviews: int
    total_checks: int
    active_models: Dict[str, Any]

@router.get("/admin/crawler/status", response_model=CrawlerStatus)
async def get_crawler_status(
    current_user: User = Depends(require_admin)
):
    """Get crawler status and metrics"""
    redis_client = get_redis()
    
    # Get crawler status from Redis
    is_running = redis_client.get("crawler:running") == "true"
    last_run = redis_client.get("crawler:last_run")
    urls_processed = int(redis_client.get("crawler:urls_processed") or 0)
    errors = int(redis_client.get("crawler:errors") or 0)
    active_workers = int(redis_client.get("crawler:active_workers") or 0)
    
    return CrawlerStatus(
        is_running=is_running,
        last_run=last_run,
        urls_processed=urls_processed,
        errors=errors,
        active_workers=active_workers
    )

@router.post("/admin/crawler/run")
async def trigger_crawl(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """Trigger immediate crawl"""
    # In production, send message to RabbitMQ to trigger crawler
    redis_client = get_redis()
    
    # Set crawler trigger flag
    redis_client.set("crawler:trigger", "true", ex=300)  # 5 minute expiry
    
    # Create audit log
    background_tasks.add_task(
        create_audit_entry,
        "crawler_triggered",
        {
            "triggered_by": str(current_user.id),
            "timestamp": time.time()
        }
    )
    
    return {"message": "Crawl triggered successfully"}

@router.get("/admin/models")
async def get_model_versions(
    current_user: User = Depends(require_admin)
):
    """Get model versions and configurations"""
    with get_db_session() as db:
        models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
        
        return [
            {
                "id": str(model.id),
                "classifier_version": model.classifier_version,
                "embedding_model": model.embedding_model,
                "llm_version": model.llm_version,
                "thresholds": model.thresholds,
                "is_active": model.is_active,
                "created_at": model.created_at.isoformat()
            }
            for model in models
        ]

@router.post("/admin/models/update")
async def update_model_config(
    model_update: ModelUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """Update model configuration"""
    with get_db_session() as db:
        # Deactivate current active model
        if model_update.is_active:
            db.query(ModelVersion).filter(ModelVersion.is_active == True).update({"is_active": False})
        
        # Create new model version
        new_model = ModelVersion(
            classifier_version=model_update.classifier_version or "v1.0.0",
            embedding_model=model_update.embedding_model or "paraphrase-multilingual-mpnet-base-v2",
            llm_version=model_update.llm_version or "llama3.2:3b",
            thresholds=model_update.thresholds or {"hi": 0.90, "ta": 0.90, "kn": 0.90, "en": 0.92},
            is_active=model_update.is_active
        )
        
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        
        # Create audit log
        background_tasks.add_task(
            create_audit_entry,
            "model_updated",
            {
                "model_id": str(new_model.id),
                "updated_by": str(current_user.id),
                "changes": model_update.dict()
            }
        )
        
        return {
            "message": "Model configuration updated successfully",
            "model_id": str(new_model.id)
        }

@router.get("/admin/audit/verify")
async def verify_audit_signature_endpoint(
    audit_id: str,
    current_user: User = Depends(require_admin)
):
    """Verify HMAC signature for an audit entry"""
    is_valid = verify_audit_signature(audit_id)
    
    return {
        "audit_id": audit_id,
        "valid": is_valid
    }

@router.get("/admin/audit/logs")
async def get_audit_logs(
    event_type: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_admin)
):
    """Get audit logs with optional filtering"""
    with get_db_session() as db:
        query = db.query(AuditLog)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": str(log.id),
                "event_type": log.event_type,
                "payload": log.payload,
                "created_at": log.created_at.isoformat(),
                "signature": log.signature
            }
            for log in logs
        ]

@router.get("/admin/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(require_admin)
):
    """Get system statistics"""
    with get_db_session() as db:
        # Get basic counts
        total_users = db.query(User).count()
        total_posts = db.query(func.count()).select_from(text("posts")).scalar()
        total_crawled_items = db.query(CrawledItem).count()
        pending_reviews = db.query(ReviewQueue).filter(ReviewQueue.status == "pending").count()
        
        # Get total checks from audit logs
        total_checks = db.query(AuditLog).filter(AuditLog.event_type == "check").count()
        
        # Get active models
        active_model = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
        active_models = {
            "classifier": active_model.classifier_version if active_model else "unknown",
            "embedding": active_model.embedding_model if active_model else "unknown",
            "llm": active_model.llm_version if active_model else "unknown",
            "thresholds": active_model.thresholds if active_model else {}
        }
        
        return SystemStats(
            total_users=total_users,
            total_posts=total_posts,
            total_crawled_items=total_crawled_items,
            pending_reviews=pending_reviews,
            total_checks=total_checks,
            active_models=active_models
        )

@router.get("/admin/health")
async def get_detailed_health(
    current_user: User = Depends(require_admin)
):
    """Get detailed system health information"""
    health_info = {
        "timestamp": time.time(),
        "services": {},
        "database": {},
        "cache": {},
        "queue": {}
    }
    
    # Check database
    try:
        with get_db_session() as db:
            db.execute("SELECT 1")
            health_info["database"]["status"] = "healthy"
            
            # Get database stats
            health_info["database"]["connections"] = "unknown"  # Would need proper monitoring
    except Exception as e:
        health_info["database"]["status"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client = get_redis()
        redis_client.ping()
        health_info["cache"]["status"] = "healthy"
        health_info["cache"]["memory_usage"] = redis_client.info("memory").get("used_memory_human", "unknown")
    except Exception as e:
        health_info["cache"]["status"] = f"unhealthy: {str(e)}"
    
    # Check Milvus
    try:
        from pymilvus import connections, Collection
        connections.connect(
            host="milvus",
            port=19530
        )
        collection = Collection("factforge_vectors")
        health_info["services"]["milvus"] = "healthy"
    except Exception as e:
        health_info["services"]["milvus"] = f"unhealthy: {str(e)}"
    
    # Check Ollama
    try:
        response = requests.get("http://ollama:11434/api/tags", timeout=5)
        if response.status_code == 200:
            health_info["services"]["ollama"] = "healthy"
        else:
            health_info["services"]["ollama"] = "unhealthy"
    except Exception as e:
        health_info["services"]["ollama"] = f"unhealthy: {str(e)}"
    
    return health_info

@router.post("/admin/reindex")
async def trigger_reindex(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """Trigger reindexing of all vectors"""
    # In production, send message to queue for reindexing
    redis_client = get_redis()
    redis_client.set("reindex:trigger", "true", ex=3600)  # 1 hour expiry
    
    # Create audit log
    background_tasks.add_task(
        create_audit_entry,
        "reindex_triggered",
        {
            "triggered_by": str(current_user.id),
            "timestamp": time.time()
        }
    )
    
    return {"message": "Reindexing triggered successfully"}

@router.delete("/admin/audit/cleanup")
async def cleanup_audit_logs(
    days: int = Query(default=365, ge=30, le=3650),
    current_user: User = Depends(require_admin)
):
    """Clean up old audit logs"""
    from ..core.audit import cleanup_old_audit_logs
    
    deleted_count = cleanup_old_audit_logs(days)
    
    # Create audit log
    create_audit_entry(
        "audit_cleanup",
        {
            "deleted_count": deleted_count,
            "retention_days": days,
            "cleaned_by": str(current_user.id)
        }
    )
    
    return {
        "message": f"Cleaned up {deleted_count} old audit logs",
        "deleted_count": deleted_count
    }

@router.get("/admin/llm/status")
async def get_llm_status(
    current_user: User = Depends(require_admin)
):
    """Get LLM provider status and information"""
    try:
        provider_info = get_llm_provider_info()
        return {
            "status": "success",
            "llm_info": provider_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get LLM status: {str(e)}")

@router.post("/admin/llm/switch")
async def switch_llm_provider_endpoint(
    provider: str = Field(..., regex="^(vertex_ai|ollama)$"),
    current_user: User = Depends(require_admin)
):
    """Switch LLM provider"""
    try:
        success = switch_llm_provider(provider)
        
        if success:
            # Create audit log
            create_audit_entry(
                "llm_provider_switch",
                {
                    "new_provider": provider,
                    "switched_by": str(current_user.id)
                }
            )
            
            return {
                "status": "success",
                "message": f"Successfully switched to {provider}",
                "provider": provider
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to switch to {provider}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch LLM provider: {str(e)}")

class LLMProviderSwitch(BaseModel):
    provider: str = Field(..., regex="^(vertex_ai|ollama)$")
