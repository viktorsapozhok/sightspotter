CREATE TABLE IF NOT EXISTS user_log(
    date timestamp,
    name text,
    action text
);

CREATE TABLE IF NOT EXISTS sights(
    sight_id integer PRIMARY KEY,
    lat float(2) NOT NULL,
    lon float(2) NOT NULL,
    event text,
    cp_id text NOT NULL,
    address text NOT NULL,
    description text,
    quest text,
    answer text,
    year integer
);

CREATE TABLE IF NOT EXISTS history(
    sight_id integer PRIMARY KEY,
    event text,
    cp_id text NOT NULL,
    history text
);

