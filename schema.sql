CREATE TYPE edge_type  AS ENUM ('counter', 'synergy');
CREATE TYPE tier_rank  AS ENUM ('S', 'A', 'B', 'C', 'D', 'E');
CREATE TYPE tier_scope AS ENUM ('ranked', 'map', 'global');
CREATE TYPE user_role  AS ENUM ('contributor', 'reviewer', 'admin');
CREATE TYPE map_environment AS ENUM (
    'canyon', 'jungle', 'snow', 'desert', 'beach',
    'volcano', 'city', 'factory', 'space', 'underwater'
);

CREATE TABLE brawlers (
    name TEXT PRIMARY KEY
);

CREATE TABLE edges (
    id       SERIAL PRIMARY KEY,
    a        TEXT NOT NULL REFERENCES brawlers(name),
    b        TEXT NOT NULL REFERENCES brawlers(name),   -- b beats / pairs with a
    type     edge_type NOT NULL,
    strength REAL
);

CREATE TABLE maps (
    name               TEXT PRIMARY KEY,
    environment        map_environment NOT NULL,
    in_ranked_rotation BOOLEAN NOT NULL DEFAULT FALSE,
    in_trophy_rotation BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE tier_lists (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    description   TEXT,
    scope         tier_scope NOT NULL,
    map_key       TEXT REFERENCES maps(name),
    patch_version TEXT
);

CREATE TABLE tier_list_entries (
    tier_list_id INT  NOT NULL REFERENCES tier_lists(id),
    brawler      TEXT NOT NULL REFERENCES brawlers(name),
    tier         tier_rank NOT NULL,
    PRIMARY KEY (tier_list_id, brawler)
);

CREATE TABLE users (
    id         TEXT PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    role       user_role NOT NULL DEFAULT 'contributor',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
