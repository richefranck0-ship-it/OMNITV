-- OMNITV database schema. Run in Supabase SQL Editor.
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  role text not null default 'viewer' check (role in ('viewer','broadcaster','advertiser','moderator','admin')),
  created_at timestamptz not null default now()
);
create table if not exists public.channels (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  category text not null,
  description text,
  stream_url text,
  approved boolean not null default false,
  created_at timestamptz not null default now()
);
create table if not exists public.submissions (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text not null,
  title text not null,
  category text not null,
  url text not null,
  description text,
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  created_at timestamptz not null default now()
);
create table if not exists public.advertisements (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  video_url text not null,
  contact_url text not null,
  placement text not null default 'home',
  active boolean not null default false,
  starts_at timestamptz,
  ends_at timestamptz,
  created_at timestamptz not null default now()
);
create table if not exists public.schedules (
  id uuid primary key default gen_random_uuid(),
  channel_name text not null,
  title text not null,
  starts_at timestamptz not null,
  ends_at timestamptz
);
create table if not exists public.comments (
  id uuid primary key default gen_random_uuid(),
  channel_id uuid references public.channels(id) on delete set null,
  display_name text not null,
  body text not null check (char_length(body) between 1 and 1000),
  created_at timestamptz not null default now()
);
create table if not exists public.analytics (
  id uuid primary key default gen_random_uuid(),
  event text not null,
  target_id text,
  created_at timestamptz not null default now()
);
create table if not exists public.favorites (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  channel_id uuid references public.channels(id) on delete cascade,
  created_at timestamptz not null default now(),
  unique(user_id,channel_id)
);

create or replace function public.is_admin()
returns boolean language sql stable security definer set search_path=public
as $$ select exists(select 1 from public.profiles where id=auth.uid() and role='admin'); $$;

alter table public.profiles enable row level security;
alter table public.channels enable row level security;
alter table public.submissions enable row level security;
alter table public.advertisements enable row level security;
alter table public.schedules enable row level security;
alter table public.comments enable row level security;
alter table public.analytics enable row level security;
alter table public.favorites enable row level security;

drop policy if exists "profile read own or admin" on public.profiles;
create policy "profile read own or admin" on public.profiles for select using (id=auth.uid() or public.is_admin());
drop policy if exists "admin manages profiles" on public.profiles;
create policy "admin manages profiles" on public.profiles for all using (public.is_admin()) with check (public.is_admin());

drop policy if exists "public read approved channels" on public.channels;
create policy "public read approved channels" on public.channels for select using (approved=true or public.is_admin());
drop policy if exists "admin manages channels" on public.channels;
create policy "admin manages channels" on public.channels for all using (public.is_admin()) with check (public.is_admin());

drop policy if exists "public submit broadcaster links" on public.submissions;
create policy "public submit broadcaster links" on public.submissions for insert with check (status='pending');
drop policy if exists "admin manages submissions" on public.submissions;
create policy "admin manages submissions" on public.submissions for all using (public.is_admin()) with check (public.is_admin());

drop policy if exists "public read active ads" on public.advertisements;
create policy "public read active ads" on public.advertisements for select using (active=true or public.is_admin());
drop policy if exists "admin manages ads" on public.advertisements;
create policy "admin manages ads" on public.advertisements for all using (public.is_admin()) with check (public.is_admin());

drop policy if exists "public reads schedule" on public.schedules;
create policy "public reads schedule" on public.schedules for select using (true);
drop policy if exists "admin manages schedule" on public.schedules;
create policy "admin manages schedule" on public.schedules for all using (public.is_admin()) with check (public.is_admin());

drop policy if exists "public reads comments" on public.comments;
create policy "public reads comments" on public.comments for select using (true);
drop policy if exists "visitors add comments" on public.comments;
create policy "visitors add comments" on public.comments for insert with check (char_length(body) between 1 and 1000);
drop policy if exists "admin moderates comments" on public.comments;
create policy "admin moderates comments" on public.comments for delete using (public.is_admin());

drop policy if exists "admin reads analytics" on public.analytics;
create policy "admin reads analytics" on public.analytics for select using (public.is_admin());
drop policy if exists "public logs analytics" on public.analytics;
create policy "public logs analytics" on public.analytics for insert with check (true);

drop policy if exists "users manage own favorites" on public.favorites;
create policy "users manage own favorites" on public.favorites for all using (user_id=auth.uid()) with check (user_id=auth.uid());

-- IMPORTANT: create the admin user via Supabase Authentication first.
-- Then run this statement with that user's actual UUID (replace UUID below).
-- Do not grant admin role based on an email supplied by a public form.
-- update public.profiles set role='admin' where id='REPLACE-WITH-AUTH-USER-UUID';
-- Add a profile row if needed:
-- insert into public.profiles(id,email,role) values ('REPLACE-WITH-AUTH-USER-UUID','YOUR_ADMIN_EMAIL','admin')
-- on conflict(id) do update set role='admin';
