CREATE TABLE public.leaderboards (
    id uuid NOT NULL,
    title character varying(128) NOT NULL,
    description character varying,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL
);

ALTER TABLE ONLY public.leaderboards
    ADD CONSTRAINT pk_leaderboards PRIMARY KEY (id);
