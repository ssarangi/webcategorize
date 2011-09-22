create table Company (
    id INTEGER PRIMARY KEY autoincrement not null,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
	crawled INTEGER DEFAULT 0
);

create table URL (
    id INTEGER PRIMARY KEY autoincrement not null,
    address TEXT NOT NULL,
    content TEXT,
	analyzed INTEGER DEFAULT 0,
	company_index INTEGER,
	FOREIGN KEY(company_index) REFERENCES Company(id)
);
