create table service_line_1 (
    id INTEGER PRIMARY KEY,
    sl1_keyword TEXT NOT NULL UNIQUE
);

create table service_line_2 (
    id INTEGER PRIMARY KEY,
    sl2_keyword TEXT NOT NULL UNIQUE
);

create table service_line_3 (
    id INTEGER PRIMARY KEY,
    sl3_keyword TEXT NOT NULL UNIQUE
);

create table keyword (
    id INTEGER PRIMARY KEY,
    keyword TEXT NOT NULL UNIQUE
);

create table relationship (
  id INTEGER PRIMARY KEY,
  sl3_index INTEGER,
  sl2_index INTEGER,
  sl1_index INTEGER,
  keyword_index INTEGER,
  FOREIGN KEY(sl3_index) REFERENCES service_line_3(id),
  FOREIGN KEY(sl2_index) REFERENCES service_line_2(id),
  FOREIGN KEY(sl1_index) REFERENCES service_line_1(id),
  FOREIGN KEY(keyword_index) REFERENCES keywords(id));
);
    
