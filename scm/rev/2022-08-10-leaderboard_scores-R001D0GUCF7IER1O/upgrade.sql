CREATE TABLE public.leaderboard_scores (
    id uuid NOT NULL,
    leaderboard_id uuid NOT NULL,
    address character varying(256) NOT NULL,
    score bigint NOT NULL,
    points_data jsonb,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL
);

ALTER TABLE ONLY public.leaderboard_scores
    ADD CONSTRAINT pk_leaderboard_scores PRIMARY KEY (id);

ALTER TABLE ONLY public.leaderboard_scores
    ADD CONSTRAINT uq_leaderboard_scores_leaderboard_id UNIQUE (leaderboard_id, address);

ALTER TABLE ONLY public.leaderboard_scores
    ADD CONSTRAINT fk_leaderboard_scores_leaderboard_id_leaderboards FOREIGN KEY (leaderboard_id) REFERENCES public.leaderboards(id) ON DELETE CASCADE;

CREATE INDEX ix_leaderboard_scores_address ON public.leaderboard_scores USING btree (address);
