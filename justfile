# SQLMesh + DuckLake pipeline commands
# Run `just` to see available commands

default:
    @just --list

# Install the DuckLake extension from the bundled package into DuckDB's extension dir
_install-ducklake:
    uv run python scripts/install_ducklake.py

# Run the full SQLMesh pipeline locally (DuckLake on disk)
run: _install-ducklake
    mkdir -p data
    uv run sqlmesh --gateway local_gateway plan --auto-apply

# Deploy the SQLMesh pipeline to MotherDuck (requires MOTHERDUCK_TOKEN)
deploy:
    @test -n "${MOTHERDUCK_TOKEN:-}" || (echo "ERROR: MOTHERDUCK_TOKEN is not set" && exit 1)
    mkdir -p data
    uv run sqlmesh --gateway motherduck plan --auto-apply

# Preview local changes without applying
plan:
    uv run sqlmesh --gateway local_gateway plan

# Run SQLMesh linter against all models
lint:
    uv run sqlmesh lint

# Run SQLMesh unit tests
test:
    uv run sqlmesh test
