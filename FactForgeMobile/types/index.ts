export interface CheckRequest {
  claim_text: string;
  language: string;
  user_id?: string;
}

export interface CheckResponse {
  id: string;
  input: string;
  inputType: 'text' | 'image' | 'url';
  request_id: string;
  verdict: 'TRUE' | 'FALSE' | 'MISLEADING' | 'UNVERIFIED' | 'PARTIALLY TRUE' | 'Likely True' | 'Likely False' | 'Unverified';
  trust_score: number;
  trustScore: number; // For backward compatibility
  confidence: number;
  keyFindings: string;
  evidence: Array<{
    title: string;
    description: string;
    relevanceScore: number;
    url: string;
  }>;
  evidence_list: Evidence[];
  sources: string[];
  reasons: string[];
  classifier_score: number;
  retrieved_ids: string[];
  latency_ms: number;
  timestamp: string;
  processingTime: number;
}

export interface Evidence {
  id: string;
  url: string;
  date: string;
  short_summary: string;
  found_by: 'crawler' | 'manual' | 'api';
  screenshot_url?: string;
  title?: string;
  snippet?: string;
}

export interface ReviewItem {
  id: string;
  snippet: string;
  heuristic_score: number;
  classifier_score: number;
  language: string;
  thumbnail: string;
  url?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export interface CrawlerStatus {
  last_run: string;
  items_fetched_last_hour: number;
  active_workers: number;
  errors: Array<{ time: string; message: string }>;
}

export interface SeedDomain {
  id: string;
  domain: string;
  tags: string[];
  last_crawled?: string;
  active: boolean;
}

export interface HeuristicRule {
  id: string;
  name: string;
  pattern: string;
  weight: number;
  active: boolean;
}

export interface WebSocketEvent {
  type: 'crawler:found' | 'check:request' | 'review:approved' | 'ingest:success' | 'classifier:high_confidence_scam';
  id: string;
  timestamp: string;
  data: any;
}

export interface User {
  id: string;
  email: string;
  role: 'user' | 'reviewer' | 'admin' | 'auditor';
  name: string;
  avatar?: string;
  bio?: string;
  verified: boolean;
  badges: string[];
  followers_count: number;
  following_count: number;
  posts_count: number;
}

export interface Metrics {
  ingestion_rate_today: number;
  flagged_items_24h: number;
  review_queue_length: number;
  precision_estimate: number;
  mean_latency_ms: number;
}

export interface Post {
  id: string;
  user: User;
  author: {
    name: string;
    avatar?: string;
  };
  claim_text: string;
  title: string;
  content: string;
  source_url?: string;
  screenshot_url?: string;
  imageUrl?: string;
  trust_score?: number;
  trustScore?: number; // For backward compatibility
  verdict?: 'TRUE' | 'FALSE' | 'MISLEADING' | 'UNVERIFIED' | 'PARTIALLY TRUE' | 'Likely True' | 'Likely False' | 'Unverified';
  confidence?: number;
  tags: string[];
  category: 'scam' | 'misinformation' | 'rumor' | 'verified' | 'needs_review';
  language: string;
  privacy: 'public' | 'group' | 'private';
  community_id?: string;
  verified_by: 'system' | 'user' | 'crawler';
  checked_on: string;
  timestamp: string;
  evidence_count: number;
  upvotes: number;
  downvotes: number;
  likes: number;
  comments: number;
  comments_count: number;
  shares: number;
  shares_count: number;
  views: number;
  views_count: number;
  trending_score: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  post_id: string;
  user: User;
  content: string;
  created_at: string;
  upvotes: number;
  downvotes: number;
}

export interface Community {
  id: string;
  name: string;
  description: string;
  avatar_url?: string;
  banner_url?: string;
  type: 'public' | 'restricted' | 'private';
  member_count: number;
  post_count: number;
  owner: User;
  moderators: User[];
  rules: string[];
  created_at: string;
  is_member: boolean;
  is_moderator: boolean;
}

export interface Notification {
  id: string;
  type: 'mention' | 'comment' | 'upvote' | 'follow' | 'group_invite' | 'review_result';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  action_url?: string;
  user?: User;
  post?: Post;
}