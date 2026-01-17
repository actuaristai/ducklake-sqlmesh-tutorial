Taken from https://www.tobikodata.com/blog/ducklake-sqlmesh-tutorial-a-hands-on
main change to make it work is to set the catalogs to be called catalog in config.yaml (instead of my_lakehouse in the website)

# Pre-requesities

- Install UV
- run `uv sync`
- install duckdb cli
- in duckdbcli, run `ATTACH 'ducklake:data/catalog.ducklake'`