CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
