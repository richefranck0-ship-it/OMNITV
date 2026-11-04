export interface Channel {
  id: string;
  name: string;
  slug: string;
  category: 'Généraliste' | 'Actualités' | 'Sport' | 'Cinéma' | 'Musique' | 'Jeunesse' | 'Découverte';
  description: string;
  stream_url: string;
  fallback_url?: string;
  logo_url: string;
  is_active: boolean;
  is_live: boolean;
  live_room?: string;
  viewer_count: number;
  country: string;
}

export interface VideoContent {
  id: string;
  title: string;
  description: string;
  category: 'Film' | 'Série' | 'Documentaire' | 'Sport' | 'Divertissement';
  poster_url: string;
  video_url: string;
  fallback_url?: string;
  duration_minutes: number;
  release_year: number;
  is_public: boolean;
  type: 'movie' | 'series';
  views: number;
}

export interface ScheduleItem {
  id: string;
  channel_name: string;
  title: string;
  category: string;
  starts_at: string;
  duration_minutes: number;
  ends_at: string;
  description: string;
}

export interface Advertisement {
  id: string;
  title: string;
  company_name: string;
  description: string;
  media_url: string;
  video_url?: string;
  media_type: 'video' | 'image';
  target_url: string;
  placement: 'player_side' | 'banner' | 'mid_roll' | 'pre_roll';
  duration_seconds: number;
  is_active: boolean;
  impressions: number;
  clicks: number;
}

export interface LiveFeedItem {
  id: string;
  channel_id: string;
  channel_name: string;
  creator_handle: string;
  creator_name: string;
  avatar_url: string;
  stream_url: string;
  fallback_url?: string;
  title: string;
  tags: string[];
  viewers: number;
  likes: number;
  category: string;
  verified: boolean;
  isCameraFeed?: boolean;
}
