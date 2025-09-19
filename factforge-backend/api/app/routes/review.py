"""
Review queue API endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.db import get_db_session
from ..core.auth import require_reviewer_or_admin
from ..core.audit import create_audit_entry
from ..core.models import User, ReviewQueue, CrawledItem

router = APIRouter()

class ReviewAction(BaseModel):
    action: str = Field(..., regex="^(approve|reject|escalate)$")
    note: Optional[str] = Field(None, max_length=1000)
    reviewer_id: str

class ReviewItem(BaseModel):
    id: str
    doc_id: str
    url: str
    domain: str
    clean_text: str
    language: str
    lang_confidence: Optional[float]
    heuristic_score: Optional[float]
    classifier_score: Optional[float]
    label: str
    created_at: str
    assigned_to: Optional[str]
    status: str
    priority: int
    note: Optional[str]

class ReviewQueueResponse(BaseModel):
    items: List[ReviewItem]
    cursor: Optional[str] = None
    has_more: bool = False
    total_pending: int

@router.get("/review/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="pending"),
    assigned_to: Optional[str] = Query(default=None),
    current_user: User = Depends(require_reviewer_or_admin)
):
    """Get review queue items"""
    with get_db_session() as db:
        # Build query
        query = db.query(ReviewQueue, CrawledItem).join(
            CrawledItem, ReviewQueue.doc_id == CrawledItem.id
        )
        
        # Apply filters
        if status:
            query = query.filter(ReviewQueue.status == status)
        
        if assigned_to:
            query = query.filter(ReviewQueue.assigned_to == assigned_to)
        
        # Order by priority and creation time
        query = query.order_by(
            ReviewQueue.priority.desc(),
            ReviewQueue.created_at.asc()
        )
        
        # Apply pagination
        if cursor:
            from datetime import datetime
            cursor_time = datetime.fromisoformat(cursor)
            query = query.filter(ReviewQueue.created_at > cursor_time)
        
        results = query.limit(limit + 1).all()
        
        # Check if there are more items
        has_more = len(results) > limit
        if has_more:
            results = results[:-1]
        
        # Generate next cursor
        next_cursor = None
        if has_more and results:
            next_cursor = results[-1][0].created_at.isoformat()
        
        # Convert to response format
        items = []
        for review_item, crawled_item in results:
            items.append(ReviewItem(
                id=str(review_item.id),
                doc_id=str(review_item.doc_id),
                url=crawled_item.url,
                domain=crawled_item.domain,
                clean_text=crawled_item.clean_text or "",
                language=crawled_item.language,
                lang_confidence=float(crawled_item.lang_confidence) if crawled_item.lang_confidence else None,
                heuristic_score=float(crawled_item.heuristic_score) if crawled_item.heuristic_score else None,
                classifier_score=float(crawled_item.classifier_score) if crawled_item.classifier_score else None,
                label=crawled_item.label,
                created_at=review_item.created_at.isoformat(),
                assigned_to=str(review_item.assigned_to) if review_item.assigned_to else None,
                status=review_item.status,
                priority=review_item.priority,
                note=review_item.note
            ))
        
        # Get total pending count
        total_pending = db.query(ReviewQueue).filter(ReviewQueue.status == "pending").count()
        
        return ReviewQueueResponse(
            items=items,
            cursor=next_cursor,
            has_more=has_more,
            total_pending=total_pending
        )

@router.post("/review/{review_id}/action")
async def review_action(
    review_id: str,
    action_data: ReviewAction,
    current_user: User = Depends(require_reviewer_or_admin)
):
    """Take action on a review item"""
    with get_db_session() as db:
        # Get review item
        review_item = db.query(ReviewQueue).filter(ReviewQueue.id == review_id).first()
        
        if not review_item:
            raise HTTPException(status_code=404, detail="Review item not found")
        
        # Get crawled item
        crawled_item = db.query(CrawledItem).filter(CrawledItem.id == review_item.doc_id).first()
        
        if not crawled_item:
            raise HTTPException(status_code=404, detail="Crawled item not found")
        
        # Update review item
        review_item.status = action_data.action
        review_item.assigned_to = current_user.id
        review_item.note = action_data.note
        
        # Update crawled item based on action
        if action_data.action == "approve":
            crawled_item.label = "scam"
            # In production, trigger embedding generation and Milvus indexing
        elif action_data.action == "reject":
            crawled_item.label = "benign"
        elif action_data.action == "escalate":
            review_item.priority = 10  # High priority
            # In production, create escalation ticket
        
        db.commit()
        
        # Create audit log
        create_audit_entry(
            "review_action",
            {
                "review_id": str(review_item.id),
                "doc_id": str(crawled_item.id),
                "action": action_data.action,
                "reviewer_id": str(current_user.id),
                "note": action_data.note
            }
        )
        
        return {
            "message": f"Review item {action_data.action}ed successfully",
            "review_id": str(review_item.id),
            "status": review_item.status
        }

@router.post("/review/{review_id}/assign")
async def assign_review(
    review_id: str,
    current_user: User = Depends(require_reviewer_or_admin)
):
    """Assign a review item to current user"""
    with get_db_session() as db:
        review_item = db.query(ReviewQueue).filter(ReviewQueue.id == review_id).first()
        
        if not review_item:
            raise HTTPException(status_code=404, detail="Review item not found")
        
        if review_item.assigned_to and review_item.assigned_to != current_user.id:
            raise HTTPException(
                status_code=400, 
                detail="Review item already assigned to another reviewer"
            )
        
        review_item.assigned_to = current_user.id
        review_item.status = "in_review"
        
        db.commit()
        
        # Create audit log
        create_audit_entry(
            "review_assigned",
            {
                "review_id": str(review_item.id),
                "assigned_to": str(current_user.id)
            }
        )
        
        return {
            "message": "Review item assigned successfully",
            "review_id": str(review_item.id),
            "assigned_to": str(current_user.id)
        }

@router.get("/review/stats")
async def get_review_stats(
    current_user: User = Depends(require_reviewer_or_admin)
):
    """Get review statistics"""
    with get_db_session() as db:
        stats = {
            "pending": db.query(ReviewQueue).filter(ReviewQueue.status == "pending").count(),
            "in_review": db.query(ReviewQueue).filter(ReviewQueue.status == "in_review").count(),
            "approved": db.query(ReviewQueue).filter(ReviewQueue.status == "approved").count(),
            "rejected": db.query(ReviewQueue).filter(ReviewQueue.status == "rejected").count(),
            "escalated": db.query(ReviewQueue).filter(ReviewQueue.status == "escalated").count(),
            "my_assigned": db.query(ReviewQueue).filter(
                ReviewQueue.assigned_to == current_user.id,
                ReviewQueue.status.in_(["pending", "in_review"])
            ).count()
        }
        
        return stats

@router.get("/review/{review_id}")
async def get_review_item(
    review_id: str,
    current_user: User = Depends(require_reviewer_or_admin)
):
    """Get detailed information about a review item"""
    with get_db_session() as db:
        review_item = db.query(ReviewQueue).filter(ReviewQueue.id == review_id).first()
        
        if not review_item:
            raise HTTPException(status_code=404, detail="Review item not found")
        
        crawled_item = db.query(CrawledItem).filter(CrawledItem.id == review_item.doc_id).first()
        
        if not crawled_item:
            raise HTTPException(status_code=404, detail="Crawled item not found")
        
        return {
            "id": str(review_item.id),
            "doc_id": str(review_item.doc_id),
            "url": crawled_item.url,
            "domain": crawled_item.domain,
            "clean_text": crawled_item.clean_text,
            "language": crawled_item.language,
            "lang_confidence": float(crawled_item.lang_confidence) if crawled_item.lang_confidence else None,
            "heuristic_score": float(crawled_item.heuristic_score) if crawled_item.heuristic_score else None,
            "classifier_score": float(crawled_item.classifier_score) if crawled_item.classifier_score else None,
            "label": crawled_item.label,
            "image_hashes": crawled_item.image_hashes,
            "whois_data": crawled_item.whois_data,
            "metadata": crawled_item.metadata,
            "created_at": review_item.created_at.isoformat(),
            "assigned_to": str(review_item.assigned_to) if review_item.assigned_to else None,
            "status": review_item.status,
            "priority": review_item.priority,
            "note": review_item.note
        }
