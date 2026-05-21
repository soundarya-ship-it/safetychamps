-- RoadSoS Database Schema
-- Run once to initialise: sqlite3 roadsos.db < schema.sql

CREATE TABLE IF NOT EXISTS contacts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    category        TEXT    NOT NULL,   -- hospital | ambulance | police | towing | puncture | pharmacy | fire
    tier            INTEGER NOT NULL,   -- 1=national, 2=state-verified, 3=local
    phone           TEXT    NOT NULL,
    phone_alt       TEXT,               -- backup number
    address         TEXT,
    lat             REAL,
    lon             REAL,
    state           TEXT,
    district        TEXT,
    country_code    TEXT    DEFAULT 'IN',
    source          TEXT,               -- osm | google_maps | nhp | nhai | manual
    confidence      INTEGER DEFAULT 50, -- 0-100
    last_verified   TEXT,               -- ISO date string
    verified_ok     INTEGER DEFAULT 0,  -- 1 if last check passed
    fail_count      INTEGER DEFAULT 0,  -- consecutive verification failures
    user_confirms   INTEGER DEFAULT 0,
    user_fails      INTEGER DEFAULT 0,
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS national_numbers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code    TEXT    NOT NULL,   -- ISO alpha-2
    country_name    TEXT    NOT NULL,
    police          TEXT,
    ambulance       TEXT,
    fire            TEXT,
    emergency       TEXT,               -- single all-services number if exists
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS verification_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id      INTEGER REFERENCES contacts(id),
    checked_at      TEXT    DEFAULT (datetime('now')),
    method          TEXT,               -- google_maps | nhp | osm | user_feedback
    result          TEXT,               -- ok | fail | unreachable | changed
    new_phone       TEXT,               -- if number changed
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS user_feedback (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id      INTEGER REFERENCES contacts(id),
    session_id      TEXT,
    worked          INTEGER NOT NULL,   -- 1=worked, 0=did not work
    comment         TEXT,
    created_at      TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS offline_cache_meta (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name     TEXT    NOT NULL,   -- e.g. "NH-44 Corridor" or "Chennai"
    region_type     TEXT,               -- highway | city | district
    bbox_south      REAL,
    bbox_north      REAL,
    bbox_west       REAL,
    bbox_east       REAL,
    cached_at       TEXT    DEFAULT (datetime('now')),
    contact_count   INTEGER DEFAULT 0
);

-- Spatial index for fast radius queries
CREATE INDEX IF NOT EXISTS idx_contacts_latlon   ON contacts(lat, lon);
CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts(category);
CREATE INDEX IF NOT EXISTS idx_contacts_tier     ON contacts(tier);
CREATE INDEX IF NOT EXISTS idx_contacts_state    ON contacts(state);
CREATE INDEX IF NOT EXISTS idx_national_country  ON national_numbers(country_code);
