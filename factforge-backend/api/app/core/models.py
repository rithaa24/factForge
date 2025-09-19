"""
Database models for FactForge backend
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, DECIMAL, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default='user')
    verified = Column(Boolean, default=False)
    badges = Column(ARRAY(String), default=[])
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    author_name = Column(String(255), nullable=False)
    author_avatar = Column(Text)
    claim_text = Column(Text, nullable=False)
    title = Column(String(500))
    content = Column(Text)
    source_url = Column(Text)
    screenshot_url = Column(Text)
    image_url = Column(Text)
    trust_score = Column(Integer)
    verdict = Column(String(50))
    confidence = Column(Integer)
    tags = Column(ARRAY(String), default=[])
    category = Column(String(50), default='needs_review')
    language = Column(String(10), nullable=False, default='en')
    privacy = Column(String(20), default='public')
    community_id = Column(UUID(as_uuid=True))
    verified_by = Column(String(50), default='user')
    checked_on = Column(DateTime(timezone=True))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    evidence_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    trending_score = Column(DECIMAL(3, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="posts")
    comments_rel = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class CrawledItem(Base):
    __tablename__ = "crawled_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False)
    raw_html_path = Column(Text)
    screenshot_path = Column(Text)
    clean_text = Column(Text)
    language = Column(String(10), nullable=False)
    lang_confidence = Column(DECIMAL(3, 2))
    translit = Column(Boolean, default=False)
    heuristic_score = Column(DECIMAL(5, 2))
    classifier_score = Column(DECIMAL(5, 2))
    label = Column(String(50), default='pending')
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    image_hashes = Column(JSON, default=[])
    whois_data = Column(JSON, default={})
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vector(Base):
    __tablename__ = "vectors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), nullable=False)
    embedding_id = Column(String(255), nullable=False)
    milvus_id = Column(String(255))
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReviewQueue(Base):
    __tablename__ = "review_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey('crawled_items.id', ondelete='CASCADE'))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    status = Column(String(50), default='pending')
    priority = Column(Integer, default=0)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    doc = relationship("CrawledItem")
    assigned_user = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    signature = Column(String(255), nullable=False)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classifier_version = Column(String(50), nullable=False)
    embedding_model = Column(String(100), nullable=False)
    llm_version = Column(String(50), nullable=False)
    thresholds = Column(JSON, nullable=False, default={})
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Community(Base):
    __tablename__ = "communities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    language = Column(String(10), nullable=False, default='en')
    member_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id', ondelete='CASCADE'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('comments.id', ondelete='CASCADE'))
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="comments_rel")
    user = relationship("User")
    parent = relationship("Comment", remote_side=[id])

# Add relationships
User.posts = relationship("Post", back_populates="user")
