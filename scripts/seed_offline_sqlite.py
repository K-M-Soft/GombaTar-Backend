import argparse
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

QUERY_TOP_500 = """
SELECT
    id,
    name_hu,
    latin_name,
    edibility,
    toxicity_level,
    market_status,
    protection_status,
    eco_type,
    identification_marks,
    determination_method,
    season_mask,
    similar_species_json,
    taxonomy_json,
    last_updated,
    observations_count
FROM mushrooms
ORDER BY observations_count DESC NULLS LAST, id ASC
LIMIT 500
"""


def _to_json_text(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _to_iso(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _fetch_top_500(engine):
    with engine.connect() as conn:
        rows = conn.execute(text(QUERY_TOP_500)).mappings().all()
    if len(rows) != 500:
        raise RuntimeError(f"Expected exactly 500 rows, got {len(rows)}")
    return rows


def _create_sqlite_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE mushrooms (
            id INTEGER NOT NULL PRIMARY KEY,
            name_hu TEXT NOT NULL,
            latin_name TEXT NOT NULL,
            edibility TEXT,
            toxicity_level TEXT,
            market_status TEXT,
            protection_status TEXT,
            eco_type TEXT,
            identification_marks TEXT,
            determination_method TEXT,
            season_mask INTEGER,
            similar_species_json TEXT,
            taxonomy_json TEXT,
            last_updated TEXT,
            observations_count INTEGER
        )
        """
    )

    cursor.execute("CREATE INDEX idx_mushrooms_obs ON mushrooms(observations_count DESC)")
    cursor.execute("CREATE INDEX idx_mushrooms_search ON mushrooms(name_hu, latin_name)")


def _insert_rows(cursor, rows):
    payload = []
    for row in rows:
        payload.append(
            (
                row["id"],
                row["name_hu"],
                row["latin_name"],
                row["edibility"],
                row["toxicity_level"],
                row["market_status"],
                row["protection_status"],
                row["eco_type"],
                row["identification_marks"],
                row["determination_method"],
                row["season_mask"],
                _to_json_text(row["similar_species_json"]),
                _to_json_text(row["taxonomy_json"]),
                _to_iso(row["last_updated"]),
                row["observations_count"],
            )
        )

    cursor.executemany(
        """
        INSERT INTO mushrooms (
            id,
            name_hu,
            latin_name,
            edibility,
            toxicity_level,
            market_status,
            protection_status,
            eco_type,
            identification_marks,
            determination_method,
            season_mask,
            similar_species_json,
            taxonomy_json,
            last_updated,
            observations_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        payload,
    )


def build_sqlite(output_path: Path):
    load_dotenv(override=True)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    engine = create_engine(database_url, pool_pre_ping=True)
    rows = _fetch_top_500(engine)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with sqlite3.connect(output_path) as sqlite_conn:
        cursor = sqlite_conn.cursor()
        _create_sqlite_schema(cursor)
        _insert_rows(cursor, rows)
        sqlite_conn.commit()

    print(f"Created SQLite database: {output_path}")
    print(f"Inserted rows: {len(rows)}")


def main():
    parser = argparse.ArgumentParser(
        description="Build offline gombatar.db with exactly the top 500 mushrooms"
    )
    parser.add_argument(
        "--output",
        default="gombatar.db",
        help="Output SQLite file path (default: gombatar.db)",
    )
    args = parser.parse_args()

    build_sqlite(Path(args.output).resolve())


if __name__ == "__main__":
    main()
