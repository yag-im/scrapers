CREATE EXTENSION pg_trgm;

DROP TABLE ag;
CREATE TABLE ag
(
    id                INTEGER primary key NOT NULL,
    name              TEXT,
    description       TEXT,
    playMode          TEXT,
    applicationCategory TEXT,
    gamePlatform      TEXT[],
    operatingSystem   TEXT[],
    author            TEXT[],
    publisher         TEXT[],
    datePublished     TEXT,
    ratingValue       FLOAT,
    ratingCount       int,
    bestRating        int,
    worstRating       int,
    genre             TEXT[]

);
CREATE INDEX trgm_ag_idx ON ag USING gist (name gist_trgm_ops);

DROP TABLE qz;
CREATE TABLE qz
(
    id               INTEGER primary key NOT NULL,
    name             text,
    rus_name         text,
    other_names      TEXT[],
    description      text,
    website          text,
    developer        TEXT[],
    publisher        text,
    date_published   text,
    lang             text,
    other_lang       TEXT[],
    platform         text,
    genre            TEXT[],
    view             text,
    control          text,
    media            TEXT[],
    license          text,
    sys_requirements text,
    engine           text,
    emulator         text,
    novel            text,
    project_status   text,
    store_link       text
);
CREATE INDEX trgm_qz_idx ON qz USING gist (name gist_trgm_ops);
