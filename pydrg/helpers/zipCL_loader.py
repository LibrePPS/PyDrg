"""Load ZIP+4 locality data into a relational database using SQLAlchemy ORM.

Supports SQLite, PostgreSQL (and other SQLAlchemy dialects) via an ORM model.
Previous implementation was SQLite-only with raw `sqlite3` usage.
"""

from __future__ import annotations

import os
import gzip
from typing import List, Iterable, Dict, Any, Union
from sqlalchemy import (
    Column,
    Integer,
    String,
    Index,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine

OPEN_END_YEAR = 9999

Base = declarative_base()


class Zip9Data(Base):
    __tablename__ = "zip9_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String, nullable=False, default="")
    zip_code = Column(String, nullable=False, index=True)
    carrier = Column(String, nullable=False)
    pricing_locality = Column(String, nullable=False)
    rural_indicator = Column(String)
    plus_four_flag = Column(String, nullable=False)
    plus_four = Column(String, nullable=False)
    part_b_payment_indicator = Column(String)
    effective_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)

    __table_args__ = (
        Index(
            "idx_zip9_key_open",
            "zip_code",
            "plus_four_flag",
            "plus_four",
            "effective_date",
            "end_date",
        ),
    )


def read_lines(path: str) -> List[str]:
    if not os.path.exists(path):
        gz = path + ".gz"
        if not os.path.exists(gz):
            return []
        path = gz
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:  # type: ignore
        return [line.rstrip("\n") for line in f]


def load_dictionaries(root: str):
    carriers = read_lines(os.path.join(root, "carriers.txt"))
    localities = read_lines(os.path.join(root, "localities.txt"))
    return carriers, localities


def ensure_engine(engine_or_url: Union[str, Engine]) -> Engine:
    if isinstance(engine_or_url, Engine):
        return engine_or_url
    return create_engine(engine_or_url, future=True)


def _iter_rows(
    root: str, carriers: List[str], localities: List[str]
) -> Iterable[Dict[str, Any]]:
    rec_dir = os.path.join(root, "records")
    if not os.path.isdir(rec_dir):
        return
    shards = sorted(
        f for f in os.listdir(rec_dir) if f.endswith(".tsv") or f.endswith(".tsv.gz")
    )
    for shard in shards:
        path = os.path.join(rec_dir, shard)
        opener = gzip.open if shard.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as fh:  # type: ignore
            for raw in fh:
                line = raw.rstrip("\n")
                if not line:
                    continue
                try:
                    zip5, plus4, sy, ey, carrier_id, locality_id = line.split("\t")
                except ValueError:
                    continue
                try:
                    carrier = carriers[int(carrier_id)]
                    locality = localities[int(locality_id)]
                except (ValueError, IndexError):
                    continue
                plus_four_flag = "0" if plus4 == "" else "1"
                plus_four_val = plus4 if plus4 else ""
                effective_date = f"{sy}-01-01"
                end_date = "9999-12-31" if ey == str(OPEN_END_YEAR) else f"{ey}-12-31"
                yield {
                    "state": "",
                    "zip_code": zip5,
                    "carrier": carrier,
                    "pricing_locality": locality,
                    "rural_indicator": "",
                    "plus_four_flag": plus_four_flag,
                    "plus_four": plus_four_val,
                    "part_b_payment_indicator": "",
                    "effective_date": effective_date,
                    "end_date": end_date,
                }


def load_records(
    root: str,
    engine_or_url: Union[str, Engine],
    batch_size: int = 5000,
    truncate: bool = False,
) -> int:
    """Load zip9 locality data.

    Parameters:
        root: directory containing carriers.txt, localities.txt, records/ shards
        engine_or_url: SQLAlchemy Engine or database URL
        batch_size: rows per batch insert
        truncate: delete existing rows before load

    Returns:
        Total inserted row count.
    """
    engine = ensure_engine(engine_or_url)
    Base.metadata.create_all(engine)
    carriers, localities = load_dictionaries(root)
    if not carriers or not localities:
        return 0
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    total = 0
    with SessionLocal() as sess:
        if truncate:
            sess.query(Zip9Data).delete()
            sess.commit()
        batch: List[Dict[str, Any]] = []
        from sqlalchemy import insert as sql_insert

        insert_stmt = sql_insert(Zip9Data)
        for rec in _iter_rows(root, carriers, localities):
            batch.append(rec)
            if len(batch) >= batch_size:
                sess.execute(insert_stmt, batch)
                sess.commit()
                total += len(batch)
                batch.clear()
        if batch:
            sess.execute(insert_stmt, batch)
            sess.commit()
            total += len(batch)
    return total


__all__ = ["load_records", "Zip9Data"]
