-- ============================================================
-- OMNITv — MIGRATION IDEMPOTENTE & TABLES COMPATIBLES SUPABASE
-- Conforme au cahier des charges : 9 tables existantes + RLS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'viewer', 'broadcaster', 'advertiser', 'moderator')),
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.channels (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE,
  category TEXT NOT NULL DEFAULT 'Actualités',
  description TEXT,
  stream_url TEXT NOT NULL,
  backup_stream_url TEXT,
  logo_url TEXT,
  approved BOOLEAN DEFAULT TRUE,
  is_active BOOLEAN DEFAULT TRUE,
  is_live BOOLEAN DEFAULT FALSE,
  live_room TEXT,
  broadcaster_key_hash TEXT,
  viewers_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.submissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  contact_email TEXT,
  title TEXT NOT NULL,
  channel_name TEXT,
  category TEXT NOT NULL,
  url TEXT,
  stream_url TEXT,
  description TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.advertisements (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  company_name TEXT,
  description TEXT,
  media_type TEXT DEFAULT 'video' CHECK (media_type IN ('video', 'image')),
  video_url TEXT,
  image_url TEXT,
  contact_url TEXT,
  target_url TEXT,
  placement TEXT DEFAULT 'side_player' CHECK (placement IN ('side_player', 'mid_roll', 'banner')),
  active BOOLEAN DEFAULT TRUE,
  is_active BOOLEAN DEFAULT TRUE,
  starts_at TIMESTAMPTZ,
  ends_at TIMESTAMPTZ,
  duration_seconds INTEGER DEFAULT 15,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.schedules (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  channel_name TEXT NOT NULL,
  channel_id UUID REFERENCES public.channels(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  category TEXT,
  description TEXT,
  poster_url TEXT,
  video_url TEXT,
  starts_at TIMESTAMPTZ NOT NULL,
  ends_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  channel_id UUID REFERENCES public.channels(id) ON DELETE CASCADE,
  display_name TEXT NOT NULL,
  body TEXT NOT NULL,
  is_broadcaster BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.videos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  channel_id UUID REFERENCES public.channels(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT DEFAULT 'Action',
  duration TEXT DEFAULT '01:30:00',
  duration_minutes INTEGER DEFAULT 90,
  year INTEGER DEFAULT 2026,
  poster_url TEXT,
  backdrop_url TEXT,
  video_url TEXT NOT NULL,
  backup_video_url TEXT,
  mid_roll_ad_timestamp INTEGER,
  is_public BOOLEAN DEFAULT TRUE,
  views INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Indexation
CREATE INDEX IF NOT EXISTS idx_channels_slug ON public.channels(slug);
CREATE INDEX IF NOT EXISTS idx_channels_is_live ON public.channels(is_live) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_schedules_time ON public.schedules(starts_at, ends_at);
CREATE INDEX IF NOT EXISTS idx_videos_public ON public.videos(is_public, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ads_active ON public.advertisements(is_active, placement);

-- RLS
ALTER TABLE public.channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.advertisements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public Read Channels" ON public.channels FOR SELECT USING (is_active = TRUE);
CREATE POLICY "Public Read Videos" ON public.videos FOR SELECT USING (is_public = TRUE);
CREATE POLICY "Public Read Schedules" ON public.schedules FOR SELECT USING (TRUE);
CREATE POLICY "Public Read Ads" ON public.advertisements FOR SELECT USING (is_active = TRUE);
CREATE POLICY "Public Read Comments" ON public.comments FOR SELECT USING (TRUE);
CREATE POLICY "Public Insert Comments" ON public.comments FOR INSERT WITH CHECK (TRUE);
