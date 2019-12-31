CREATE TABLE IF NOT EXISTS user_log(
    date timestamp,
    name text,
    action text
);

CREATE TABLE IF NOT EXISTS routes(
    event text,
    year integer,
    route text,
    PRIMARY KEY (event, year)
);

CREATE TABLE IF NOT EXISTS sights(
    sight_id integer,
    lat float(2) NOT NULL,
    lon float(2) NOT NULL,
    event text,
    cp_id text NOT NULL,
    address text NOT NULL,
    description text,
    quest text,
    answer text,
    year integer,
    PRIMARY KEY (event, cp_id)
);

CREATE TABLE IF NOT EXISTS history(
    sight_id integer,
    event text,
    cp_id text NOT NULL,
    history text,
    PRIMARY KEY (event, cp_id)
);
