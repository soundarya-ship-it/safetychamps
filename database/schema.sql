-- RoadSoS Database Schema
-- Run once to initialise: sqlite3 roadsos.db < schema.sql

CREATE TABLE IF NOT EXISTS contacts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    tier            INTEGER NOT NULL,
    phone           TEXT    NOT NULL,
    phone_alt       TEXT,
    address         TEXT,
    lat             REAL,
    lon             REAL,
    state           TEXT,
    district        TEXT,
    country_code    TEXT    DEFAULT 'IN',
    source          TEXT,
    confidence      INTEGER DEFAULT 50,
    last_verified   TEXT,
    verified_ok     INTEGER DEFAULT 0,
    fail_count      INTEGER DEFAULT 0,
    user_confirms   INTEGER DEFAULT 0,
    user_fails      INTEGER DEFAULT 0,
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS national_numbers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code    TEXT    NOT NULL UNIQUE,
    country_name    TEXT    NOT NULL,
    police          TEXT,
    ambulance       TEXT,
    fire            TEXT,
    emergency       TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS verification_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id      INTEGER REFERENCES contacts(id),
    checked_at      TEXT    DEFAULT (datetime('now')),
    method          TEXT,
    result          TEXT,
    new_phone       TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS user_feedback (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id      INTEGER REFERENCES contacts(id),
    session_id      TEXT,
    worked          INTEGER NOT NULL,
    comment         TEXT,
    created_at      TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS offline_cache_meta (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name     TEXT    NOT NULL,
    region_type     TEXT,
    bbox_south      REAL,
    bbox_north      REAL,
    bbox_west       REAL,
    bbox_east       REAL,
    cached_at       TEXT    DEFAULT (datetime('now')),
    contact_count   INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_contacts_latlon   ON contacts(lat, lon);
CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts(category);
CREATE INDEX IF NOT EXISTS idx_contacts_tier     ON contacts(tier);
CREATE INDEX IF NOT EXISTS idx_contacts_state    ON contacts(state);
CREATE INDEX IF NOT EXISTS idx_national_country  ON national_numbers(country_code);
