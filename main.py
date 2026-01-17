import duckdb
import ibis


ibis.options.interactive = True

# use this code snippet to show the connection pane on the right. note need to diconnect to reduce conflicts.
connection_pane = duckdb.connect()
connection_pane.install_extension("ducklake")
connection_pane.sql("ATTACH 'ducklake:data/catalog.ducklake'")
%connection_show connection_pane
connection_pane.close()


def main():
    print("Showing example of how to use with ibis")
    con = ibis.duckdb.connect(extensions="ducklake")
    con.attach("ducklake:data/catalog.ducklake", read_only=True)
    events = con.table('events', database='catalog.raw')
    stg_events = con.table('stg_events', database='catalog.staging')
    daily_revenue = con.table('daily_revenue', database='catalog.analytics')
    con.list_tables(database='catalog.raw')
    con.list_tables(database='catalog.staging')
    con.list_tables(database='catalog.analytics')
    con.list_databases(catalog='catalog')
    con.list_catalogs()
    con.disconnect()


if __name__ == "__main__":
    main()
