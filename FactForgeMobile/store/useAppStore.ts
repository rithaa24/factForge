import { create } from 'zustand';
import { User, WebSocketEvent, Metrics } from '../types';

interface AppState {
  user: User | null;
  currentLanguage: 'en' | 'hi' | 'ta';
  events: WebSocketEvent[];
  metrics: Metrics | null;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setLanguage: (language: 'en' | 'hi' | 'ta') => void;
  addEvent: (event: WebSocketEvent) => void;
  setMetrics: (metrics: Metrics) => void;
  setLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: {
    id: 'demo-user',
    email: 'admin@factforge.demo',
    role: 'admin',
    name: 'Demo Admin',
    verified: true,
    badges: ['admin', 'fact-checker'],
    followers_count: 0,
    following_count: 0,
    posts_count: 0
  },
  currentLanguage: 'en',
  events: [],
  metrics: null,
  isLoading: false,
  
  setUser: (user) => set({ user }),
  setLanguage: (language) => set({ currentLanguage: language }),
  addEvent: (event) => set((state) => ({ 
    events: [event, ...state.events.slice(0, 49)] // Keep last 50 events
  })),
  setMetrics: (metrics) => set({ metrics }),
  setLoading: (loading) => set({ isLoading: loading })
}));
