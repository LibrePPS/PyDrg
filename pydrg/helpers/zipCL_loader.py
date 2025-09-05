"""Rebuild SQLite database from dictionary-coded flatdata export (in-package)."""
from __future__ import annotations

import os
import gzip
import sqlite3
from typing import List

OPEN_END_YEAR = 9999

DDL = '''CREATE TABLE IF NOT EXISTS zip9_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL,
    carrier TEXT NOT NULL,
    pricing_locality TEXT NOT NULL,
    rural_indicator TEXT,
    plus_four_flag TEXT NOT NULL,
    plus_four TEXT NOT NULL,
    part_b_payment_indicator TEXT,
    effective_date TEXT NOT NULL,
    end_date TEXT NOT NULL
);'''

INSERT_SQL = '''INSERT INTO zip9_data(
    state, zip_code, carrier, pricing_locality, rural_indicator,
    plus_four_flag, plus_four, part_b_payment_indicator, effective_date, end_date
) VALUES(?,?,?,?,?,?,?,?,?,?)'''


def read_lines(path: str) -> List[str]:
    if not os.path.exists(path):
        gz = path + '.gz'
        if not os.path.exists(gz):
            return []
        path = gz
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as f:  # type: ignore
        return [line.rstrip('\n') for line in f]


def load_dictionaries(root: str):
    carriers = read_lines(os.path.join(root, 'carriers.txt'))
    localities = read_lines(os.path.join(root, 'localities.txt'))
    return carriers, localities


def ensure_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute(DDL)
    return conn


def load_records(root: str, db_path: str):
    carriers, localities = load_dictionaries(root)
    conn = ensure_db(db_path)
    cur = conn.cursor()
    batch = []
    batch_size = 5000
    rec_dir = os.path.join(root, 'records')
    shards = sorted([f for f in os.listdir(rec_dir) if f.endswith('.tsv') or f.endswith('.tsv.gz')])
    for shard in shards:
        path = os.path.join(rec_dir, shard)
        opener = gzip.open if shard.endswith('.gz') else open
        with opener(path, 'rt', encoding='utf-8') as f:  # type: ignore
            for line in f:
                line = line.rstrip('\n')
                if not line:
                    continue
                zip5, plus4, sy, ey, carrier_id, locality_id = line.split('\t')
                carrier = carriers[int(carrier_id)]
                locality = localities[int(locality_id)]
                plus_four_flag = '0' if plus4 == '' else '1'
                plus_four_val = plus4 if plus4 != '' else ''
                effective_date = f"{sy}-01-01"
                end_date = '9999-12-31' if ey == str(OPEN_END_YEAR) else f"{ey}-12-31"
                batch.append(('', zip5, carrier, locality, '', plus_four_flag, plus_four_val, '', effective_date, end_date))
                if len(batch) >= batch_size:
                    cur.executemany(INSERT_SQL, batch)
                    batch.clear()
    if batch:
        cur.executemany(INSERT_SQL, batch)
    conn.commit()
    cur.close()
    conn.execute('CREATE INDEX IF NOT EXISTS idx_zip9_key_open ON zip9_data(zip_code, plus_four_flag, plus_four, effective_date, end_date)')
    conn.commit()
    conn.close()


__all__ = ['load_records']
