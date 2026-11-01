-- OMNITV : migration pour pages de chaîne, archives et directs LiveKit
-- À exécuter dans Supabase SQL Editor APRÈS le schema.sql existant.

alter table public.channels add column if not exists slug text;
alter table public.submissions add column if not exists channel_name text;
alter table public.submissions add column if not exists stream_url text;
alter table public.submissions add column if not exists contact_email text;
alter table public.channels add column if not exists logo_url text;
alter table public.channels add column if not exists is_active boolean not null default true;
alter table public.channels add column if not exists is_live boolean not null default false;
alter table public.channels add column if not exists live_room text;
alter table public.channels add column if not exists broadcaster_key_hash text;

update public.channels
set slug = trim(both '-' from regexp_replace(lower(name), '[^a-z0-9]+', '-', 'g'))
where slug is null;

update public.channels set live_room = 'omnitv-' || id::text where live_room is null;
create unique index if not exists channels_slug_unique on public.channels(slug);

create table if not exists public.videos (
  id uuid primary key default gen_random_uuid(),
  channel_id uuid not null references public.channels(id) on delete cascade,
  title text not null,
  description text,
  video_url text not null,
  is_public boolean not null default true,
  created_at timestamptz not null default now()
);
alter table public.videos enable row level security;
drop policy if exists "public reads channel archives" on public.videos;
create policy "public reads channel archives" on public.videos
for select using (is_public = true);
drop policy if exists "admin manages channel archives" on public.videos;
create policy "admin manages channel archives" on public.videos
for all using (public.is_admin()) with check (public.is_admin());

-- Compatibilité avec les noms de colonnes utilisés par l'interface Flask
alter table public.advertisements add column if not exists company_name text;
alter table public.advertisements add column if not exists target_url text;
alter table public.advertisements add column if not exists is_active boolean not null default false;

-- Pour les anciennes lignes, conserver les chaînes déjà approuvées.
update public.channels set is_active = approved where approved is not null;
