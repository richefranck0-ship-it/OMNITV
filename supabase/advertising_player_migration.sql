-- OMNITv : publicités dans les lecteurs et annonces à la fin des films
-- À exécuter une seule fois dans Supabase SQL Editor après les migrations précédentes.

alter table public.advertisements
  add column if not exists company_name text,
  add column if not exists target_url text,
  add column if not exists is_active boolean not null default false,
  add column if not exists placement text not null default 'all';

-- Conserver les anciennes publicités actives et les afficher à côté des programmes.
update public.advertisements
set company_name = coalesce(company_name, title),
    target_url = coalesce(target_url, contact_url),
    is_active = (is_active or active),
    placement = case when placement in ('end', 'all') then placement else 'all' end;

alter table public.advertisements alter column placement set default 'all';

create index if not exists advertisements_active_placement_idx
on public.advertisements (is_active, placement, created_at desc);

-- Les règles RLS existantes "public read active ads" et "admin manages ads"
-- doivent rester activées sur cette table.
