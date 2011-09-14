create table Company (
    id INTEGER PRIMARY KEY autoincrement not null,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL
);

create table URL (
    id INTEGER PRIMARY KEY autoincrement not null,
    address TEXT NOT NULL UNIQUE,
    content BLOB NOT NULL
);
