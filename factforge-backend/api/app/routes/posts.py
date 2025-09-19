"""
Posts and feed API endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.db import get_db_session
from ..core.auth import get_current_user, require_role
from ..core.audit import create_audit_entry
from ..core.models import User, Post, Community, Comment

router = APIRouter()

class PostCreate(BaseModel):
    claim_text: str = Field(..., min_length=1, max_length=5000)
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, max_length=10000)
    source_url: Optional[str] = None
    screenshot_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default=[])
    category: str = Field(default="needs_review")
    language: str = Field(default="en")
    privacy: str = Field(default="public")
    community_id: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    author_name: str
    author_avatar: Optional[str]
    claim_text: str
    title: Optional[str]
    content: Optional[str]
    source_url: Optional[str]
    screenshot_url: Optional[str]
    image_url: Optional[str]
    trust_score: Optional[int]
    verdict: Optional[str]
    confidence: Optional[int]
    tags: List[str]
    category: str
    language: str
    privacy: str
    verified_by: str
    checked_on: Optional[str]
    timestamp: str
    evidence_count: int
    upvotes: int
    downvotes: int
    likes: int
    comments: int
    comments_count: int
    shares: int
    shares_count: int
    views: int
    views_count: int
    trending_score: float
    created_at: str
    updated_at: str

class FeedResponse(BaseModel):
    posts: List[PostResponse]
    cursor: Optional[str] = None
    has_more: bool = False

@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a new post"""
    with get_db_session() as db:
        # Create post
        post = Post(
            user_id=current_user.id,
            author_name=current_user.name,
            author_avatar=None,  # Would be set from user profile
            claim_text=post_data.claim_text,
            title=post_data.title,
            content=post_data.content,
            source_url=post_data.source_url,
            screenshot_url=post_data.screenshot_url,
            image_url=post_data.image_url,
            tags=post_data.tags,
            category=post_data.category,
            language=post_data.language,
            privacy=post_data.privacy,
            community_id=post_data.community_id,
            verified_by="user"
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        # Create audit log
        background_tasks.add_task(
            create_audit_entry,
            "post_created",
            {
                "post_id": str(post.id),
                "user_id": str(current_user.id),
                "category": post.category,
                "language": post.language
            }
        )
        
        return PostResponse(
            id=str(post.id),
            author_name=post.author_name,
            author_avatar=post.author_avatar,
            claim_text=post.claim_text,
            title=post.title,
            content=post.content,
            source_url=post.source_url,
            screenshot_url=post.screenshot_url,
            image_url=post.image_url,
            trust_score=post.trust_score,
            verdict=post.verdict,
            confidence=post.confidence,
            tags=post.tags,
            category=post.category,
            language=post.language,
            privacy=post.privacy,
            verified_by=post.verified_by,
            checked_on=post.checked_on.isoformat() if post.checked_on else None,
            timestamp=post.timestamp.isoformat(),
            evidence_count=post.evidence_count,
            upvotes=post.upvotes,
            downvotes=post.downvotes,
            likes=post.likes,
            comments=post.comments,
            comments_count=post.comments_count,
            shares=post.shares,
            shares_count=post.shares_count,
            views=post.views,
            views_count=post.views_count,
            trending_score=float(post.trending_score),
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )

@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    filter: str = Query(default="trending", regex="^(trending|following|global)$"),
    cursor: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    language: Optional[str] = Query(default=None),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get feed posts"""
    with get_db_session() as db:
        query = db.query(Post).filter(Post.privacy == "public")
        
        # Apply language filter
        if language:
            query = query.filter(Post.language == language)
        
        # Apply sorting based on filter
        if filter == "trending":
            query = query.order_by(Post.trending_score.desc(), Post.created_at.desc())
        elif filter == "following":
            # In production, filter by followed users
            query = query.order_by(Post.created_at.desc())
        else:  # global
            query = query.order_by(Post.created_at.desc())
        
        # Apply pagination
        if cursor:
            # Simple cursor-based pagination using created_at
            from datetime import datetime
            cursor_time = datetime.fromisoformat(cursor)
            query = query.filter(Post.created_at < cursor_time)
        
        posts = query.limit(limit + 1).all()
        
        # Check if there are more posts
        has_more = len(posts) > limit
        if has_more:
            posts = posts[:-1]
        
        # Generate next cursor
        next_cursor = None
        if has_more and posts:
            next_cursor = posts[-1].created_at.isoformat()
        
        # Convert to response format
        post_responses = []
        for post in posts:
            post_responses.append(PostResponse(
                id=str(post.id),
                author_name=post.author_name,
                author_avatar=post.author_avatar,
                claim_text=post.claim_text,
                title=post.title,
                content=post.content,
                source_url=post.source_url,
                screenshot_url=post.screenshot_url,
                image_url=post.image_url,
                trust_score=post.trust_score,
                verdict=post.verdict,
                confidence=post.confidence,
                tags=post.tags,
                category=post.category,
                language=post.language,
                privacy=post.privacy,
                verified_by=post.verified_by,
                checked_on=post.checked_on.isoformat() if post.checked_on else None,
                timestamp=post.timestamp.isoformat(),
                evidence_count=post.evidence_count,
                upvotes=post.upvotes,
                downvotes=post.downvotes,
                likes=post.likes,
                comments=post.comments,
                comments_count=post.comments_count,
                shares=post.shares,
                shares_count=post.shares_count,
                views=post.views,
                views_count=post.views_count,
                trending_score=float(post.trending_score),
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat()
            ))
        
        return FeedResponse(
            posts=post_responses,
            cursor=next_cursor,
            has_more=has_more
        )

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get a specific post by ID"""
    with get_db_session() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check privacy
        if post.privacy == "private" and (not current_user or str(post.user_id) != str(current_user.id)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return PostResponse(
            id=str(post.id),
            author_name=post.author_name,
            author_avatar=post.author_avatar,
            claim_text=post.claim_text,
            title=post.title,
            content=post.content,
            source_url=post.source_url,
            screenshot_url=post.screenshot_url,
            image_url=post.image_url,
            trust_score=post.trust_score,
            verdict=post.verdict,
            confidence=post.confidence,
            tags=post.tags,
            category=post.category,
            language=post.language,
            privacy=post.privacy,
            verified_by=post.verified_by,
            checked_on=post.checked_on.isoformat() if post.checked_on else None,
            timestamp=post.timestamp.isoformat(),
            evidence_count=post.evidence_count,
            upvotes=post.upvotes,
            downvotes=post.downvotes,
            likes=post.likes,
            comments=post.comments,
            comments_count=post.comments_count,
            shares=post.shares,
            shares_count=post.shares_count,
            views=post.views,
            views_count=post.views_count,
            trending_score=float(post.trending_score),
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )

@router.post("/posts/{post_id}/vote")
async def vote_post(
    post_id: str,
    vote: int = Field(..., ge=-1, le=1),
    current_user: User = Depends(get_current_user)
):
    """Vote on a post (1 for upvote, -1 for downvote, 0 to remove vote)"""
    with get_db_session() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # In production, implement proper voting logic with user_votes table
        if vote == 1:
            post.upvotes += 1
        elif vote == -1:
            post.downvotes += 1
        
        db.commit()
        
        return {"message": "Vote recorded", "upvotes": post.upvotes, "downvotes": post.downvotes}

@router.post("/posts/{post_id}/share")
async def share_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """Share a post"""
    with get_db_session() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post.shares += 1
        post.shares_count += 1
        db.commit()
        
        return {"message": "Post shared", "shares": post.shares}

@router.get("/communities")
async def get_communities(
    language: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get list of communities"""
    with get_db_session() as db:
        query = db.query(Community).filter(Community.is_public == True)
        
        if language:
            query = query.filter(Community.language == language)
        
        communities = query.limit(limit).all()
        
        return [
            {
                "id": str(community.id),
                "name": community.name,
                "description": community.description,
                "language": community.language,
                "member_count": community.member_count,
                "created_at": community.created_at.isoformat()
            }
            for community in communities
        ]
