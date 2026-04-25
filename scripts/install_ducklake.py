"""Install the DuckLake extension from the bundled pip package into DuckDB's extension dir."""
import shutil
import pathlib
import duckdb
import duckdb_extension_ducklake as ext_pkg

version = duckdb.__version__
src = pathlib.Path(ext_pkg.__file__).parent / "extensions" / f"v{version}" / "ducklake.duckdb_extension"
target = pathlib.Path.home() / ".duckdb" / "extensions" / f"v{version}" / "linux_amd64" / "ducklake.duckdb_extension"

if target.exists():
    print(f"DuckLake extension already installed at {target}")
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)
    print(f"DuckLake extension installed at {target}")
