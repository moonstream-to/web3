CREATE TABLE public.dropper_claimants (
    id uuid NOT NULL,
    dropper_claim_id uuid NOT NULL,
    address character varying(256) NOT NULL,
    amount bigint NOT NULL,
    added_by character varying(256) NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    signature character varying,
    raw_amount character varying
);

ALTER TABLE ONLY public.dropper_claimants
    ADD CONSTRAINT pk_dropper_claimants PRIMARY KEY (id);

ALTER TABLE ONLY public.dropper_claimants
    ADD CONSTRAINT uq_dropper_claimants_dropper_claim_id UNIQUE (dropper_claim_id, address);

ALTER TABLE ONLY public.dropper_claimants
    ADD CONSTRAINT uq_dropper_claimants_id UNIQUE (id);

ALTER TABLE ONLY public.dropper_claimants
    ADD CONSTRAINT fk_dropper_claimants_dropper_claim_id_dropper_claims FOREIGN KEY (dropper_claim_id) REFERENCES public.dropper_claims(id) ON DELETE CASCADE;

CREATE INDEX ix_dropper_claimants_added_by ON public.dropper_claimants USING btree (added_by);

CREATE INDEX ix_dropper_claimants_address ON public.dropper_claimants USING btree (address);

CREATE INDEX ix_dropper_claimants_signature ON public.dropper_claimants USING btree (signature);
