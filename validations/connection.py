from pathlib import Path

import ibis


def get_connection(read_only: bool = True) -> ibis.BaseBackend:
    """Return an ibis DuckDB connection with the local DuckLake catalog attached."""
    catalog_path = _find_catalog()
    con = ibis.duckdb.connect(extensions=["ducklake"])
    con.attach(f"ducklake:{catalog_path}", name="my_lakehouse", read_only=read_only)
    return con


def _find_catalog() -> Path:
    """Walk up the directory tree to find data/catalog.ducklake."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        candidate = current / "data" / "catalog.ducklake"
        if candidate.exists():
            return candidate
        current = current.parent
    raise FileNotFoundError("Could not locate data/catalog.ducklake")
