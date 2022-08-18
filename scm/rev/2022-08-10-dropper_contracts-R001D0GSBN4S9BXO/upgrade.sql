CREATE TABLE public.dropper_contracts (
    id uuid NOT NULL,
    blockchain character varying(128) NOT NULL,
    address character varying(256),
    created_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, statement_timestamp()) NOT NULL,
    title character varying(128),
    description character varying,
    image_uri character varying
);

ALTER TABLE ONLY public.dropper_contracts
    ADD CONSTRAINT pk_dropper_contracts PRIMARY KEY (id);

ALTER TABLE ONLY public.dropper_contracts
    ADD CONSTRAINT uq_dropper_contracts_blockchain UNIQUE (blockchain, address);

ALTER TABLE ONLY public.dropper_contracts
    ADD CONSTRAINT uq_dropper_contracts_id UNIQUE (id);

CREATE INDEX ix_dropper_contracts_address ON public.dropper_contracts USING btree (address);
