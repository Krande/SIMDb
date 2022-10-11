from __future__ import annotations
from dataclasses import dataclass
import edgedb
import pathlib


@dataclass
class SimDb:
    name: str
    client: edgedb.Client | edgedb.AsyncIOClient = None
    db_schema_dir: str | pathlib.Path = "dbschema"

