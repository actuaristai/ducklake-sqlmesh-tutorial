import ibis


def main():
    print("Hello from ducklake-sqlmesh-tutorial!")
    con = ibis.duckdb.connect(extensions="ducklake")
    con.attach("ducklake:data/catalog.ducklake")
    events = con.table('events', database='catalog.raw')
    stg_events = con.table('stg_events', database='catalog.staging')
    daily_revenue = con.table('daily_revenue', database='catalog.analytics')


if __name__ == "__main__":
    main()
