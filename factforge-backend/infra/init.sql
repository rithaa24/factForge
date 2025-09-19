-- FactForge Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'reviewer', 'admin')),
    verified BOOLEAN DEFAULT FALSE,
    badges TEXT[] DEFAULT '{}',
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Posts table
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    author_name VARCHAR(255) NOT NULL,
    author_avatar TEXT,
    claim_text TEXT NOT NULL,
    title VARCHAR(500),
    content TEXT,
    source_url TEXT,
    screenshot_url TEXT,
    image_url TEXT,
    trust_score INTEGER,
    verdict VARCHAR(50) CHECK (verdict IN ('TRUE', 'FALSE', 'MISLEADING', 'UNVERIFIED', 'PARTIALLY TRUE', 'Likely True', 'Likely False', 'Unverified')),
    confidence INTEGER,
    tags TEXT[] DEFAULT '{}',
    category VARCHAR(50) DEFAULT 'needs_review' CHECK (category IN ('scam', 'misinformation', 'rumor', 'verified', 'needs_review')),
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    privacy VARCHAR(20) DEFAULT 'public' CHECK (privacy IN ('public', 'group', 'private')),
    community_id UUID,
    verified_by VARCHAR(50) DEFAULT 'user' CHECK (verified_by IN ('system', 'user', 'crawler')),
    checked_on TIMESTAMP WITH TIME ZONE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evidence_count INTEGER DEFAULT 0,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    trending_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crawled items table
CREATE TABLE crawled_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    domain VARCHAR(255) NOT NULL,
    raw_html_path TEXT,
    screenshot_path TEXT,
    clean_text TEXT,
    language VARCHAR(10) NOT NULL,
    lang_confidence DECIMAL(3,2),
    translit BOOLEAN DEFAULT FALSE,
    heuristic_score DECIMAL(5,2),
    classifier_score DECIMAL(5,2),
    label VARCHAR(50) DEFAULT 'pending' CHECK (label IN ('scam', 'benign', 'pending')),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_hashes JSONB DEFAULT '[]',
    whois_data JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vectors table for Milvus integration
CREATE TABLE vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id UUID NOT NULL,
    embedding_id VARCHAR(255) NOT NULL,
    milvus_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Review queue table
CREATE TABLE review_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id UUID REFERENCES crawled_items(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'approved', 'rejected', 'escalated')),
    priority INTEGER DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    signature VARCHAR(255) NOT NULL
);

-- Model versions table
CREATE TABLE model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    classifier_version VARCHAR(50) NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    llm_version VARCHAR(50) NOT NULL,
    thresholds JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Communities table
CREATE TABLE communities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    member_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comments table
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_posts_language ON posts(language);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_posts_verdict ON posts(verdict);
CREATE INDEX idx_posts_category ON posts(category);
CREATE INDEX idx_posts_trending_score ON posts(trending_score);

CREATE INDEX idx_crawled_items_language ON crawled_items(language);
CREATE INDEX idx_crawled_items_label ON crawled_items(label);
CREATE INDEX idx_crawled_items_ingested_at ON crawled_items(ingested_at);
CREATE INDEX idx_crawled_items_domain ON crawled_items(domain);

CREATE INDEX idx_vectors_doc_id ON vectors(doc_id);
CREATE INDEX idx_vectors_milvus_id ON vectors(milvus_id);

CREATE INDEX idx_review_queue_status ON review_queue(status);
CREATE INDEX idx_review_queue_assigned_to ON review_queue(assigned_to);
CREATE INDEX idx_review_queue_created_at ON review_queue(created_at);

CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);

-- Create full-text search indexes
CREATE INDEX idx_posts_content_fts ON posts USING gin(to_tsvector('english', content));
CREATE INDEX idx_crawled_items_clean_text_fts ON crawled_items USING gin(to_tsvector('english', clean_text));

-- Insert default admin user
INSERT INTO users (id, name, email, role, verified, badges) VALUES 
('00000000-0000-0000-0000-000000000001', 'Admin User', 'admin@factforge.com', 'admin', TRUE, ARRAY['admin', 'fact-checker']);

-- Insert default model version
INSERT INTO model_versions (classifier_version, embedding_model, llm_version, thresholds, is_active) VALUES 
('v1.0.0', 'paraphrase-multilingual-mpnet-base-v2', 'llama3.2:3b', '{"hi": 0.90, "ta": 0.90, "kn": 0.90, "en": 0.92}', TRUE);

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_review_queue_updated_at BEFORE UPDATE ON review_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_communities_updated_at BEFORE UPDATE ON communities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
