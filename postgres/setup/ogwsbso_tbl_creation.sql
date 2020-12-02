CREATE TABLE public.ogwsbso
(
    id serial NOT NULL,
    ticker_symbol character(25) COLLATE pg_catalog."default" NOT NULL,
    text character(999) COLLATE pg_catalog."default" NOT NULL,
    positive character(2) COLLATE pg_catalog."default",
    "timestamp" timestamp without time zone,
    CONSTRAINT ogwsb_so_pkey PRIMARY KEY (id)
);
