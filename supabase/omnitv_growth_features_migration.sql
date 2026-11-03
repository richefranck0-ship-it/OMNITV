-- OMNITv : programmation, affiches et coupures publicitaires
-- Exécuter une seule fois dans Supabase SQL Editor.

alter table public.advertisements
  add column if not exists image_url text;

alter table public.videos
  add column if not exists image_url text,
  add column if not exists duration_minutes integer,
  add column if not exists midroll_after_seconds integer;

alter table public.schedules
  add column if not exists duration_minutes integer,
  add column if not exists image_url text,
  add column if not exists video_url text;

-- Permet les publicités latérales, de milieu de film et de fin.
update public.advertisements set placement='all' where placement is null or placement not in ('all','end','midroll');

alter table public.advertisements alter column video_url drop not null;
