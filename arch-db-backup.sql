-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.cases (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  reviewed_at timestamp with time zone DEFAULT now(),
  submitter_id bigint NOT NULL UNIQUE,
  reviewer_id bigint,
  status USER-DEFINED NOT NULL DEFAULT 'pending'::"Blueprint Status",
  ai_decision text,
  reviewer_comment text,
  submitted_at timestamp with time zone NOT NULL DEFAULT now(),
  blueprint_path text NOT NULL,
  CONSTRAINT cases_pkey PRIMARY KEY (id),
  CONSTRAINT cases_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.users(id),
  CONSTRAINT cases_submitter_id_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id)
);
CREATE TABLE public.guidelines (
  code text NOT NULL,
  title text NOT NULL,
  description text,
  category text,
  CONSTRAINT guidelines_pkey PRIMARY KEY (code)
);
CREATE TABLE public.notifications (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  message text,
  read boolean,
  title USER-DEFINED,
  CONSTRAINT notifications_pkey PRIMARY KEY (id),
  CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.users (
  name text NOT NULL,
  email text NOT NULL DEFAULT ''::text UNIQUE,
  role USER-DEFINED NOT NULL,
  joined_at timestamp without time zone DEFAULT now(),
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  password text,
  badge_number bigint NOT NULL UNIQUE,
  CONSTRAINT users_pkey PRIMARY KEY (id)
);
CREATE TABLE public.violations (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  case_id bigint NOT NULL,
  guideline_code text NOT NULL UNIQUE,
  CONSTRAINT violations_pkey PRIMARY KEY (id),
  CONSTRAINT violations_guideline_code_fkey FOREIGN KEY (guideline_code) REFERENCES public.guidelines(code),
  CONSTRAINT violations_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id)
);