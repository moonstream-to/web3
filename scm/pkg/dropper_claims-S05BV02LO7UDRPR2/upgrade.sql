CREATE TABLE public.dropper_claims (
    id uuid NOT NULL,
    dropper_contract_id uuid NOT NULL,
    claim_id bigint,
    title character varying(128),
    description character varying,
    terminus_address character varying(256),
    terminus_pool_id bigint,
    claim_block_deadline bigint,
    active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL
);

ALTER TABLE ONLY public.dropper_claims
    ADD CONSTRAINT pk_dropper_claims PRIMARY KEY (id);

ALTER TABLE ONLY public.dropper_claims
    ADD CONSTRAINT uq_dropper_claims_id UNIQUE (id);

ALTER TABLE ONLY public.dropper_claims
    ADD CONSTRAINT fk_dropper_claims_dropper_contract_id_dropper_contracts FOREIGN KEY (dropper_contract_id) REFERENCES public.dropper_contracts(id) ON DELETE CASCADE;

CREATE INDEX ix_dropper_claims_terminus_address ON public.dropper_claims USING btree (terminus_address);

CREATE INDEX ix_dropper_claims_terminus_pool_id ON public.dropper_claims USING btree (terminus_pool_id);

CREATE UNIQUE INDEX uq_dropper_claims_dropper_contract_id_claim_id ON public.dropper_claims USING btree (dropper_contract_id, claim_id) WHERE ((claim_id IS NOT NULL) AND (active = true));
