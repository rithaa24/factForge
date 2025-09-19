import { CheckRequest, CheckResponse, ReviewItem, CrawlerStatus, SeedDomain, HeuristicRule, Metrics, Post, Comment, Community, Notification, User } from '../types';
import { API_CONFIG, API_ENDPOINTS, DEFAULT_HEADERS, ERROR_MESSAGES, DEBUG_CONFIG } from './config';
import { httpClient } from './httpClient';

const API_BASE = API_CONFIG.BASE_URL;

// Mock data
const mockEvidence = [
  {
    id: 'E1',
    url: 'https://scam-detector.example/report-123',
    date: '2024-01-15',
    short_summary: 'Identical UPI scam pattern detected with 94% similarity',
    found_by: 'crawler' as const,
    screenshot_url: 'https://images.pexels.com/photos/5483064/pexels-photo-5483064.jpeg?auto=compress&cs=tinysrgb&w=400',
    title: 'UPI Payment Scam Alert',
    snippet: 'This message asks for immediate payment via UPI with urgent language typical of scams.'
  },
  {
    id: 'E2', 
    url: 'https://factcheck.org/verified-claims/payment-scams',
    date: '2024-01-10',
    short_summary: 'Government advisory about UPI payment scams',
    found_by: 'manual' as const,
    title: 'Official Payment Scam Advisory',
    snippet: 'Government agencies warn about fraudulent messages requesting immediate payments.'
  }
];

const mockReviewItems: ReviewItem[] = [
  {
    id: 'item1',
    snippet: 'Send ₹1000 to UPI abc@upi to claim your lottery prize of ₹50,000!',
    heuristic_score: 0.85,
    classifier_score: 0.78,
    language: 'hi',
    thumbnail: 'https://images.pexels.com/photos/5483064/pexels-photo-5483064.jpeg?auto=compress&cs=tinysrgb&w=150',
    url: 'https://suspicious-site.example/lottery',
    status: 'pending',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 'item2',
    snippet: 'Urgent: Your account will be blocked. Click here to verify immediately.',
    heuristic_score: 0.92,
    classifier_score: 0.86,
    language: 'en',
    thumbnail: 'https://images.pexels.com/photos/5691659/pexels-photo-5691659.jpeg?auto=compress&cs=tinysrgb&w=150',
    url: 'https://fake-bank.example/verify',
    status: 'pending',
    created_at: '2024-01-15T09:15:00Z'
  }
];

const mockSeedDomains: SeedDomain[] = [
  {
    id: '1',
    domain: 'whatsapp-forwards.social',
    tags: ['whatsapp-forward', 'social'],
    last_crawled: '2024-01-15T08:00:00Z',
    active: true
  },
  {
    id: '2', 
    domain: 'suspicious-news.blog',
    tags: ['blog', 'misinformation'],
    last_crawled: '2024-01-14T22:30:00Z',
    active: true
  }
];

// Mock posts data
const mockPosts: Post[] = [
  {
    id: 'post1',
    user: {
      id: 'user1',
      name: 'Priya Sharma',
      email: 'priya@example.com',
      role: 'user',
      avatar: 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=150',
      verified: true,
      badges: ['fact-checker', 'top-reporter'],
      followers_count: 1250,
      following_count: 340,
      posts_count: 89
    },
    author: {
      name: 'Priya Sharma',
      avatar: 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=150'
    },
    claim_text: 'Urgent: Send ₹1000 to UPI abc@upi to claim your lottery prize of ₹50,000! Limited time offer.',
    title: 'UPI Lottery Scam Alert',
    content: 'Urgent: Send ₹1000 to UPI abc@upi to claim your lottery prize of ₹50,000! Limited time offer.',
    source_url: 'https://example.com/scam',
    screenshot_url: 'https://images.pexels.com/photos/5483064/pexels-photo-5483064.jpeg?auto=compress&cs=tinysrgb&w=400',
    imageUrl: 'https://images.pexels.com/photos/5483064/pexels-photo-5483064.jpeg?auto=compress&cs=tinysrgb&w=400',
    trust_score: 15,
    trustScore: 15,
    verdict: 'Likely False',
    confidence: 95,
    tags: ['scam', 'upi', 'lottery', 'urgent'],
    category: 'scam',
    language: 'hi',
    privacy: 'public',
    verified_by: 'system',
    checked_on: '2024-01-15T10:30:00Z',
    timestamp: '2024-01-15T10:30:00Z',
    evidence_count: 3,
    upvotes: 45,
    downvotes: 2,
    likes: 45,
    comments: 12,
    comments_count: 12,
    shares: 8,
    shares_count: 8,
    views: 234,
    views_count: 234,
    trending_score: 0.85,
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 'post2',
    user: {
      id: 'user2',
      name: 'Raj Kumar',
      email: 'raj@example.com',
      role: 'user',
      avatar: 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=150',
      verified: false,
      badges: ['community-helper'],
      followers_count: 89,
      following_count: 156,
      posts_count: 23
    },
    author: {
      name: 'Raj Kumar',
      avatar: 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=150'
    },
    claim_text: 'Government announces new COVID-19 vaccination drive for children aged 12-15. Registration starts tomorrow.',
    title: 'COVID-19 Vaccination Drive for Children',
    content: 'Government announces new COVID-19 vaccination drive for children aged 12-15. Registration starts tomorrow.',
    source_url: 'https://mohfw.gov.in/covid-vaccination',
    trust_score: 92,
    trustScore: 92,
    verdict: 'Likely True',
    confidence: 88,
    tags: ['covid', 'vaccination', 'government', 'children'],
    category: 'verified',
    language: 'en',
    privacy: 'public',
    verified_by: 'crawler',
    checked_on: '2024-01-15T09:15:00Z',
    timestamp: '2024-01-15T09:15:00Z',
    evidence_count: 5,
    upvotes: 128,
    downvotes: 3,
    likes: 128,
    comments: 34,
    comments_count: 34,
    shares: 67,
    shares_count: 67,
    views: 1456,
    views_count: 1456,
    trending_score: 0.92,
    created_at: '2024-01-15T09:15:00Z',
    updated_at: '2024-01-15T09:15:00Z'
  },
  {
    id: 'post3',
    user: {
      id: 'user3',
      name: 'Sarah Johnson',
      email: 'sarah@example.com',
      role: 'reviewer',
      avatar: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150',
      verified: true,
      badges: ['expert-reviewer', 'health-specialist'],
      followers_count: 2340,
      following_count: 890,
      posts_count: 156
    },
    author: {
      name: 'Sarah Johnson',
      avatar: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150'
    },
    claim_text: 'New study claims drinking lemon water cures diabetes. Doctors hate this one simple trick!',
    title: 'Lemon Water Diabetes Cure - Fact Check',
    content: 'New study claims drinking lemon water cures diabetes. Doctors hate this one simple trick!',
    trust_score: 25,
    trustScore: 25,
    verdict: 'Likely False',
    confidence: 85,
    tags: ['health', 'misinformation', 'diabetes', 'fake-cure'],
    category: 'misinformation',
    language: 'en',
    privacy: 'public',
    verified_by: 'user',
    checked_on: '2024-01-15T08:45:00Z',
    timestamp: '2024-01-15T08:45:00Z',
    evidence_count: 4,
    upvotes: 89,
    downvotes: 5,
    likes: 89,
    comments: 23,
    comments_count: 23,
    shares: 12,
    shares_count: 12,
    views: 567,
    views_count: 567,
    trending_score: 0.78,
    created_at: '2024-01-15T08:45:00Z',
    updated_at: '2024-01-15T08:45:00Z'
  }
];

const mockCommunities: Community[] = [
  {
    id: 'comm1',
    name: 'Scam Alerts India',
    description: 'Community dedicated to sharing and verifying scam alerts across India',
    avatar_url: 'https://images.pexels.com/photos/5483064/pexels-photo-5483064.jpeg?auto=compress&cs=tinysrgb&w=150',
    type: 'public',
    member_count: 12450,
    post_count: 1890,
    owner: {
      id: 'user1',
      name: 'Priya Sharma',
      email: 'priya@example.com',
      role: 'user',
      verified: true,
      badges: ['fact-checker'],
      followers_count: 1250,
      following_count: 340,
      posts_count: 89
    },
    moderators: [],
    rules: [
      'Only post verified scam alerts',
      'Include evidence when possible',
      'Be respectful to all members',
      'No spam or self-promotion'
    ],
    created_at: '2023-06-15T10:00:00Z',
    is_member: true,
    is_moderator: false
  },
  {
    id: 'comm2',
    name: 'Fact Checkers United',
    description: 'Private community for verified fact-checkers and journalists',
    type: 'private',
    member_count: 234,
    post_count: 567,
    owner: {
      id: 'user3',
      name: 'Sarah Johnson',
      email: 'sarah@example.com',
      role: 'reviewer',
      verified: true,
      badges: ['expert-reviewer'],
      followers_count: 2340,
      following_count: 890,
      posts_count: 156
    },
    moderators: [],
    rules: [
      'Verified credentials required',
      'Share reliable sources only',
      'Maintain professional standards'
    ],
    created_at: '2023-08-20T14:30:00Z',
    is_member: false,
    is_moderator: false
  }
];

const mockHeuristicRules: HeuristicRule[] = [
  {
    id: '1',
    name: 'UPI Payment Request',
    pattern: '(send|transfer).*(₹|rupees|rs).*upi',
    weight: 0.8,
    active: true
  },
  {
    id: '2',
    name: 'Urgent Action Required',
    pattern: '(urgent|immediately|expire|block)',
    weight: 0.6,
    active: true
  }
];

// Simulate API calls with delays
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  async checkContent(request: CheckRequest): Promise<CheckResponse> {
    try {
      // Try real API first
      const response = await httpClient.post<CheckResponse>(API_ENDPOINTS.CHECK, request);
      
      if (DEBUG_CONFIG.ENABLE_LOGGING) {
        console.log('✅ Real API response received for fact-check');
      }
      
      return response.data;
    } catch (error) {
      if (DEBUG_CONFIG.ENABLE_LOGGING) {
        console.log('⚠️ Real API failed, falling back to mock data:', error);
      }
      
      // Fallback to mock data
      await delay(2000); // Simulate processing time
      
      // Mock different responses based on content
      const isScam = request.claim_text.toLowerCase().includes('upi') || 
                     request.claim_text.toLowerCase().includes('send money') ||
                     request.claim_text.toLowerCase().includes('urgent');
      
      const trust_score = isScam ? Math.floor(Math.random() * 30) + 10 : Math.floor(Math.random() * 30) + 70;
      const verdict = trust_score < 40 ? 'Likely False' : trust_score > 70 ? 'Likely True' : 'Unverified';
      
      return {
        id: `check_${Date.now()}`,
        input: request.claim_text,
        inputType: 'text',
        request_id: `req_${Date.now()}`,
        verdict,
        trust_score,
        trustScore: trust_score,
        confidence: Math.floor(Math.random() * 30) + 70,
        keyFindings: isScam ? 'This content appears to be a scam based on pattern analysis.' : 'This content has been verified against reliable sources.',
        evidence: mockEvidence.map(e => ({
          title: e.title,
          description: e.short_summary,
          relevanceScore: Math.random(),
          url: e.url
        })),
        evidence_list: mockEvidence,
        sources: mockEvidence.map(e => e.url),
        reasons: isScam ? [
          'Content matches known scam patterns with 94% similarity',
          'Domain created recently (within 30 days)',
          'No credible sources support this claim'
        ] : [
          'Content verified by multiple reliable sources',
          'No contradictory evidence found',
          'Matches established factual patterns'
        ],
        classifier_score: isScam ? 0.94 : 0.12,
        retrieved_ids: ['E1', 'E2'],
        latency_ms: 2100 + Math.floor(Math.random() * 1000),
        timestamp: new Date().toISOString(),
        processingTime: 2100 + Math.floor(Math.random() * 1000)
      };
    }
  },

  async getReviewQueue(limit = 20): Promise<{ items: ReviewItem[]; cursor?: string }> {
    await delay(500);
    return {
      items: mockReviewItems,
      cursor: 'next_cursor_123'
    };
  },

  async submitReviewAction(id: string, action: 'approve' | 'reject' | 'escalate', note?: string): Promise<void> {
    await delay(300);
    console.log(`Review action: ${action} for item ${id}`, note);
  },

  async getCrawlerStatus(): Promise<CrawlerStatus> {
    await delay(400);
    return {
      last_run: '2024-01-15T12:01:03Z',
      items_fetched_last_hour: 243,
      active_workers: 6,
      errors: [
        { time: '2024-01-15T11:45:00Z', message: 'Rate limit hit on domain suspicious-site.example' }
      ]
    };
  },

  async getSeedDomains(): Promise<SeedDomain[]> {
    await delay(300);
    return mockSeedDomains;
  },

  async addSeedDomain(domain: Omit<SeedDomain, 'id'>): Promise<SeedDomain> {
    await delay(400);
    return { ...domain, id: Date.now().toString() };
  },

  async getHeuristicRules(): Promise<HeuristicRule[]> {
    await delay(300);
    return mockHeuristicRules;
  },

  async addHeuristicRule(rule: Omit<HeuristicRule, 'id'>): Promise<HeuristicRule> {
    await delay(400);
    return { ...rule, id: Date.now().toString() };
  },

  async previewHeuristics(text: string): Promise<{ matches: Array<{ rule: string; confidence: number }> }> {
    await delay(600);
    const matches = mockHeuristicRules
      .filter(rule => rule.active)
      .map(rule => ({
        rule: rule.name,
        confidence: Math.random() * rule.weight
      }))
      .filter(match => match.confidence > 0.3);
      
    return { matches };
  },

  // Social platform endpoints
  async getFeed(filter = 'trending', cursor?: string): Promise<{ posts: Post[]; cursor?: string }> {
    await delay(800);
    return {
      posts: mockPosts,
      cursor: 'next_cursor_456'
    };
  },

  async createPost(postData: Partial<Post>): Promise<Post> {
    await delay(600);
    const newPost: Post = {
      id: `post_${Date.now()}`,
      user: {
        id: 'current_user',
        name: 'Current User',
        email: 'user@example.com',
        role: 'user',
        verified: false,
        badges: [],
        followers_count: 0,
        following_count: 0,
        posts_count: 1
      },
      author: {
        name: 'Current User',
        avatar: undefined
      },
      claim_text: postData.claim_text || '',
      title: postData.title || postData.claim_text || '',
      content: postData.content || postData.claim_text || '',
      source_url: postData.source_url,
      screenshot_url: postData.screenshot_url,
      imageUrl: postData.imageUrl,
      trust_score: postData.trust_score,
      trustScore: postData.trustScore,
      verdict: postData.verdict,
      confidence: postData.confidence,
      tags: postData.tags || [],
      category: postData.category || 'needs_review',
      language: postData.language || 'en',
      privacy: postData.privacy || 'public',
      verified_by: 'user',
      checked_on: new Date().toISOString(),
      timestamp: new Date().toISOString(),
      evidence_count: 0,
      upvotes: 0,
      downvotes: 0,
      likes: 0,
      comments: 0,
      comments_count: 0,
      shares: 0,
      shares_count: 0,
      views: 0,
      views_count: 0,
      trending_score: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...postData
    };
    return newPost;
  },

  async votePost(postId: string, vote: 1 | -1): Promise<{ upvotes: number; downvotes: number }> {
    await delay(300);
    return {
      upvotes: Math.floor(Math.random() * 100) + 50,
      downvotes: Math.floor(Math.random() * 10) + 2
    };
  },

  async getCommunities(): Promise<Community[]> {
    await delay(500);
    return mockCommunities;
  },

  async getCommunity(id: string): Promise<Community> {
    await delay(400);
    return mockCommunities.find(c => c.id === id) || mockCommunities[0];
  },

  async joinCommunity(id: string): Promise<void> {
    await delay(400);
  },

  async getNotifications(): Promise<Notification[]> {
    await delay(300);
    return [
      {
        id: 'notif1',
        type: 'upvote',
        title: 'Your post was upvoted',
        message: 'Priya Sharma upvoted your scam alert',
        read: false,
        created_at: '2024-01-15T11:30:00Z'
      },
      {
        id: 'notif2',
        type: 'comment',
        title: 'New comment on your post',
        message: 'Someone commented on your UPI scam alert',
        read: true,
        created_at: '2024-01-15T10:15:00Z'
      }
    ];
  },

  async getMetrics(): Promise<Metrics> {
    await delay(500);
    return {
      ingestion_rate_today: 1247,
      flagged_items_24h: 89,
      review_queue_length: 23,
      precision_estimate: 0.94,
      mean_latency_ms: 2150
    };
  }
};